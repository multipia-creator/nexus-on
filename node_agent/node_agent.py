"""
Windows Node Agent (Prototype)
- 페어링 (Enrollment)
- Poll 기반 명령 수신 (WSS는 미래 구현)
- 로컬 폴더 스캔 + 텍스트 추출
- 리포트 업로드

Usage:
    python node_agent.py --enroll ABC123
    python node_agent.py --run
"""
import argparse
import json
import os
import time
import uuid
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests


class NodeAgent:
    """Windows Node Agent"""
    
    def __init__(self, config_path: str = "node_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.base_url = self.config.get("base_url", "http://localhost:8000")
        self.node_id = self.config.get("node_id", f"node-win-{uuid.uuid4().hex[:8]}")
        self.node_token = self.config.get("node_token")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load config from JSON file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_config(self) -> None:
        """Save config to JSON file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    # ============================================================
    # Pairing (Enrollment)
    # ============================================================
    
    def enroll(self, pairing_code: str) -> bool:
        """
        페어링 (노드 등록)
        
        Args:
            pairing_code: 6자리 페어링 코드
        
        Returns:
            성공 여부
        """
        print(f"[Node Agent] Enrolling with pairing code: {pairing_code}")
        
        hostname = platform.node()
        os_version = platform.platform()
        agent_version = "1.0.0-prototype"
        
        payload = {
            "pairing_code": pairing_code,
            "node_id": self.node_id,
            "hostname": hostname,
            "os_version": os_version,
            "agent_version": agent_version
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/node/pairing/claim",
                json=payload,
                timeout=10
            )
            
            if resp.status_code == 200:
                data = resp.json()
                self.node_token = data["node_token"]
                self.config["node_id"] = self.node_id
                self.config["node_token"] = self.node_token
                self.config["tenant_id"] = data["tenant_id"]
                self._save_config()
                
                print(f"[Node Agent] ✅ Enrollment successful!")
                print(f"  Node ID: {self.node_id}")
                print(f"  Tenant ID: {data['tenant_id']}")
                return True
            else:
                print(f"[Node Agent] ❌ Enrollment failed: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            print(f"[Node Agent] ❌ Enrollment error: {e}")
            return False
    
    # ============================================================
    # Poll Commands
    # ============================================================
    
    def poll_commands(self) -> List[Dict[str, Any]]:
        """
        Poll 방식으로 명령 가져오기 (30초 타임아웃)
        
        Returns:
            명령 목록
        """
        if not self.node_token:
            print("[Node Agent] ❌ Not enrolled. Run --enroll first.")
            return []
        
        try:
            resp = requests.get(
                f"{self.base_url}/node/poll",
                params={"node_id": self.node_id, "node_token": self.node_token},
                timeout=35  # 30초 + 5초 여유
            )
            
            if resp.status_code == 200:
                data = resp.json()
                commands = data.get("commands", [])
                if commands:
                    print(f"[Node Agent] Received {len(commands)} command(s)")
                return commands
            else:
                print(f"[Node Agent] ❌ Poll failed: {resp.status_code}")
                return []
        except Exception as e:
            print(f"[Node Agent] ❌ Poll error: {e}")
            return []
    
    # ============================================================
    # Execute Commands
    # ============================================================
    
    def execute_command(self, command: Dict[str, Any]) -> None:
        """
        명령 실행
        
        Args:
            command: 명령 페이로드 (command_id, type, params)
        """
        command_id = command["command_id"]
        command_type = command["type"]
        params = command.get("params", {})
        
        print(f"[Node Agent] Executing command: {command_type} (id={command_id})")
        
        # 진행 상황 리포트
        self._send_report(command_id, "in_progress", progress={"status": "started"})
        
        if command_type == "local.folder.ingest":
            self._execute_folder_ingest(command_id, params)
        else:
            print(f"[Node Agent] ⚠️  Unknown command type: {command_type}")
            self._send_report(command_id, "failed", error=f"Unknown command type: {command_type}")
    
    def _execute_folder_ingest(self, command_id: str, params: Dict[str, Any]) -> None:
        """
        로컬 폴더 스캔 + 텍스트 추출
        
        Args:
            command_id: 명령 ID
            params: { folder, extensions }
        """
        folder = params.get("folder", ".")
        extensions = params.get("extensions", "txt,md,pdf").split(",")
        
        print(f"[Node Agent] Scanning folder: {folder}")
        print(f"[Node Agent] Extensions: {extensions}")
        
        # 진행 상황 리포트
        self._send_report(command_id, "in_progress", progress={"scanned": 0, "total": 0})
        
        try:
            folder_path = Path(folder)
            if not folder_path.exists():
                raise FileNotFoundError(f"Folder not found: {folder}")
            
            # 파일 수집
            all_files = []
            for ext in extensions:
                all_files.extend(folder_path.rglob(f"*.{ext.strip()}"))
            
            total_files = len(all_files)
            print(f"[Node Agent] Found {total_files} file(s)")
            
            # 텍스트 추출 (간단한 프로토타입: .txt만)
            chunks = []
            for idx, file_path in enumerate(all_files[:50], 1):  # 최대 50개
                try:
                    if file_path.suffix.lower() in ['.txt', '.md']:
                        text = file_path.read_text(encoding='utf-8', errors='ignore')
                        doc_id = f"{file_path.name}::{uuid.uuid4().hex[:8]}::chunk0"
                        
                        chunks.append({
                            "doc_id": doc_id,
                            "text": text[:10000],  # 최대 10KB
                            "meta": {
                                "source_path": str(file_path),
                                "source_ext": file_path.suffix,
                                "source_size": file_path.stat().st_size
                            }
                        })
                    
                    # 진행 상황 업데이트 (5개마다)
                    if idx % 5 == 0:
                        self._send_report(
                            command_id, 
                            "in_progress", 
                            progress={"scanned": idx, "total": total_files}
                        )
                except Exception as e:
                    print(f"[Node Agent] ⚠️  Failed to extract {file_path}: {e}")
            
            # 최종 리포트
            result = {
                "ingested": len(chunks),
                "total": total_files,
                "chunks": chunks
            }
            
            self._send_report(command_id, "completed", result=result)
            print(f"[Node Agent] ✅ Completed: {len(chunks)} chunks extracted")
        
        except Exception as e:
            print(f"[Node Agent] ❌ Folder ingest failed: {e}")
            self._send_report(command_id, "failed", error=str(e))
    
    # ============================================================
    # Report Upload
    # ============================================================
    
    def _send_report(
        self, 
        command_id: str, 
        status: str,
        progress: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> None:
        """
        리포트 업로드
        
        Args:
            command_id: 명령 ID
            status: "in_progress" | "completed" | "failed"
            progress: 진행 상황 (선택)
            result: 최종 결과 (선택)
            error: 에러 메시지 (선택)
        """
        payload = {
            "node_id": self.node_id,
            "command_id": command_id,
            "status": status,
            "progress": progress,
            "result": result,
            "error": error
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/node/report",
                json=payload,
                timeout=10
            )
            
            if resp.status_code == 200:
                print(f"[Node Agent] Report sent: {status}")
            else:
                print(f"[Node Agent] ⚠️  Report failed: {resp.status_code}")
        except Exception as e:
            print(f"[Node Agent] ⚠️  Report error: {e}")
    
    # ============================================================
    # Main Loop
    # ============================================================
    
    def run(self) -> None:
        """
        메인 루프 (Poll 기반)
        """
        print(f"[Node Agent] Starting...")
        print(f"  Node ID: {self.node_id}")
        print(f"  Base URL: {self.base_url}")
        print(f"  Press Ctrl+C to stop")
        
        if not self.node_token:
            print("[Node Agent] ❌ Not enrolled. Run --enroll first.")
            return
        
        try:
            while True:
                # Poll 명령
                commands = self.poll_commands()
                
                # 명령 실행
                for command in commands:
                    self.execute_command(command)
                
                # 5초 대기 (Poll이 30초 타임아웃이므로 짧은 간격)
                if not commands:
                    time.sleep(5)
        
        except KeyboardInterrupt:
            print("\n[Node Agent] Stopped by user")


def main():
    parser = argparse.ArgumentParser(description="Windows Node Agent")
    parser.add_argument("--enroll", type=str, help="Enroll with pairing code")
    parser.add_argument("--run", action="store_true", help="Run agent (poll mode)")
    parser.add_argument("--base-url", type=str, default="http://localhost:8000", help="Backend API base URL")
    
    args = parser.parse_args()
    
    agent = NodeAgent()
    agent.base_url = args.base_url
    
    if args.enroll:
        agent.enroll(args.enroll)
    elif args.run:
        agent.run()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
