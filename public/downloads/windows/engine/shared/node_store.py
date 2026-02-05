"""
Node State Store - Redis-backed node state management
Stores node enrollment, connection state, and command queue.
"""
import json
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
import redis


class NodeStore:
    """Redis-backed store for Windows Node state management"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.r = redis.from_url(redis_url, decode_responses=True)
    
    # ============================================================
    # Pairing (Enrollment)
    # ============================================================
    
    def create_pairing_code(self, tenant_id: str, ttl_seconds: int = 300) -> str:
        """
        페어링 코드 생성 (6자리 대문자+숫자, 5분 TTL)
        
        Args:
            tenant_id: 테넌트 ID (org:project)
            ttl_seconds: TTL (기본 300초 = 5분)
        
        Returns:
            pairing_code: "ABC123" 형식
        """
        # 6자리 랜덤 코드 생성 (충돌 방지)
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(10):  # 최대 10회 재시도
            code = ''.join(secrets.choice(alphabet) for _ in range(6))
            key = self._k_pairing_code(code)
            
            # SETNX로 중복 방지
            created = self.r.setnx(key, json.dumps({
                "tenant_id": tenant_id,
                "created_at": self._utc_iso(),
                "expires_at": self._utc_iso(seconds=ttl_seconds)
            }))
            
            if created:
                self.r.expire(key, ttl_seconds)
                return code
        
        raise RuntimeError("Failed to generate unique pairing code after 10 attempts")
    
    def claim_pairing_code(
        self, 
        pairing_code: str, 
        node_id: str, 
        node_info: Dict[str, Any]
    ) -> Optional[str]:
        """
        페어링 코드 사용 (일회용)
        
        Args:
            pairing_code: 페어링 코드
            node_id: 노드 ID (예: node-win-001)
            node_info: 노드 정보 (hostname, os, version 등)
        
        Returns:
            tenant_id if success, None if code invalid/expired
        """
        key = self._k_pairing_code(pairing_code)
        data_raw = self.r.get(key)
        
        if not data_raw:
            return None
        
        data = json.loads(data_raw)
        tenant_id = data["tenant_id"]
        
        # 코드 삭제 (일회용)
        self.r.delete(key)
        
        # 노드 등록
        node_key = self._k_node(tenant_id, node_id)
        self.r.hset(node_key, mapping={
            "node_id": node_id,
            "tenant_id": tenant_id,
            "status": "enrolled",
            "enrolled_at": self._utc_iso(),
            "info": json.dumps(node_info)
        })
        
        # 테넌트의 노드 목록에 추가
        nodes_key = self._k_tenant_nodes(tenant_id)
        self.r.sadd(nodes_key, node_id)
        
        return tenant_id
    
    # ============================================================
    # Node Connection State
    # ============================================================
    
    def set_node_state(
        self, 
        tenant_id: str, 
        node_id: str, 
        status: str,
        connection_type: Optional[str] = None
    ) -> None:
        """
        노드 연결 상태 업데이트
        
        Args:
            tenant_id: 테넌트 ID
            node_id: 노드 ID
            status: "online" | "offline" | "error"
            connection_type: "wss" | "poll" | None
        """
        node_key = self._k_node(tenant_id, node_id)
        updates = {
            "status": status,
            "last_seen": self._utc_iso()
        }
        
        if connection_type:
            updates["connection_type"] = connection_type
        
        self.r.hset(node_key, mapping=updates)
        
        # TTL 갱신 (노드가 오프라인되어도 30일간 보관)
        self.r.expire(node_key, 30 * 86400)
    
    def get_node_state(self, tenant_id: str, node_id: str) -> Optional[Dict[str, Any]]:
        """노드 상태 조회"""
        node_key = self._k_node(tenant_id, node_id)
        data = self.r.hgetall(node_key)
        
        if not data:
            return None
        
        # info 필드는 JSON 파싱
        if "info" in data:
            data["info"] = json.loads(data["info"])
        
        return data
    
    def list_tenant_nodes(
        self, 
        tenant_id: str, 
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        테넌트의 모든 노드 목록 조회
        
        Args:
            tenant_id: 테넌트 ID
            status_filter: "online" | "offline" | None (전체)
        
        Returns:
            노드 목록
        """
        nodes_key = self._k_tenant_nodes(tenant_id)
        node_ids = self.r.smembers(nodes_key)
        
        nodes = []
        for node_id in node_ids:
            node = self.get_node_state(tenant_id, node_id)
            if node and (not status_filter or node.get("status") == status_filter):
                nodes.append(node)
        
        return nodes
    
    # ============================================================
    # Command Queue (Node → Backend)
    # ============================================================
    
    def push_command(
        self, 
        tenant_id: str, 
        node_id: str, 
        command: Dict[str, Any]
    ) -> None:
        """
        노드에게 명령 전송 (Redis List에 추가)
        
        Args:
            tenant_id: 테넌트 ID
            node_id: 노드 ID
            command: 명령 페이로드 (command_id, type, params 등)
        """
        commands_key = self._k_node_commands(tenant_id, node_id)
        command["created_at"] = self._utc_iso()
        
        # RPUSH: 큐의 끝에 추가
        self.r.rpush(commands_key, json.dumps(command))
        
        # TTL 설정 (24시간)
        self.r.expire(commands_key, 86400)
    
    def pop_commands(
        self, 
        tenant_id: str, 
        node_id: str, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        노드가 명령을 가져감 (Poll 방식)
        
        Args:
            tenant_id: 테넌트 ID
            node_id: 노드 ID
            limit: 최대 가져갈 명령 수
        
        Returns:
            명령 목록 (FIFO 순서)
        """
        commands_key = self._k_node_commands(tenant_id, node_id)
        
        commands = []
        for _ in range(limit):
            # LPOP: 큐의 앞에서 제거
            cmd_raw = self.r.lpop(commands_key)
            if not cmd_raw:
                break
            
            try:
                commands.append(json.loads(cmd_raw))
            except json.JSONDecodeError:
                # 파싱 실패 시 스킵
                continue
        
        return commands
    
    # ============================================================
    # Redis Key Helpers
    # ============================================================
    
    def _k_pairing_code(self, code: str) -> str:
        """nexus:node:pairing:{code}"""
        return f"nexus:node:pairing:{code}"
    
    def _k_node(self, tenant_id: str, node_id: str) -> str:
        """nexus:node:{tenant_id}:{node_id}:state"""
        return f"nexus:node:{tenant_id}:{node_id}:state"
    
    def _k_tenant_nodes(self, tenant_id: str) -> str:
        """nexus:node:{tenant_id}:nodes (Set)"""
        return f"nexus:node:{tenant_id}:nodes"
    
    def _k_node_commands(self, tenant_id: str, node_id: str) -> str:
        """nexus:node:{tenant_id}:{node_id}:commands (List)"""
        return f"nexus:node:{tenant_id}:{node_id}:commands"
    
    # ============================================================
    # Utilities
    # ============================================================
    
    def _utc_iso(self, seconds: int = 0) -> str:
        """UTC ISO 8601 timestamp"""
        dt = datetime.now(timezone.utc)
        if seconds:
            dt += timedelta(seconds=seconds)
        return dt.isoformat()
