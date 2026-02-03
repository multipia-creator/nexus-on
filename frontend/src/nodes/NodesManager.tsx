import { useState, useEffect } from 'react';
import type { NodeState, PairingCodeResponse, NodeListResponse, NodeCommandRequest } from './types';

interface NodesManagerProps {
  baseUrl: string;
  orgId: string;
  projectId: string;
  apiKey?: string;
  onError?: (error: string) => void;
}

/**
 * Windows Node 관리 컴포넌트
 * - 페어링 코드 생성
 * - 노드 목록 조회
 * - 노드 상태 표시
 * - 명령 전송 (로컬 폴더 스캔 등)
 */
export function NodesManager({ baseUrl, orgId, projectId, apiKey, onError }: NodesManagerProps) {
  const [nodes, setNodes] = useState<NodeState[]>([]);
  const [loading, setLoading] = useState(false);
  const [pairingCode, setPairingCode] = useState<string | null>(null);
  const [pairingExpiry, setPairingExpiry] = useState<number | null>(null);

  // 노드 목록 조회
  const fetchNodes = async () => {
    setLoading(true);
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'x-org-id': orgId,
        'x-project-id': projectId,
      };
      if (apiKey) {
        headers['x-api-key'] = apiKey;
      }

      const res = await fetch(`${baseUrl}/node/list`, { headers });
      if (!res.ok) {
        throw new Error(`Failed to fetch nodes: ${res.status}`);
      }

      const data: NodeListResponse = await res.json();
      setNodes(data.nodes);
    } catch (err: any) {
      onError?.(err.message || 'Failed to fetch nodes');
    } finally {
      setLoading(false);
    }
  };

  // 페어링 코드 생성
  const createPairingCode = async () => {
    setLoading(true);
    setPairingCode(null);
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'x-org-id': orgId,
        'x-project-id': projectId,
      };
      if (apiKey) {
        headers['x-api-key'] = apiKey;
      }

      const res = await fetch(`${baseUrl}/node/pairing/create`, {
        method: 'POST',
        headers,
      });

      if (!res.ok) {
        throw new Error(`Failed to create pairing code: ${res.status}`);
      }

      const data: PairingCodeResponse = await res.json();
      setPairingCode(data.pairing_code);
      setPairingExpiry(Date.now() + data.expires_in * 1000);

      // 5분 후 자동으로 코드 초기화
      setTimeout(() => {
        setPairingCode(null);
        setPairingExpiry(null);
      }, data.expires_in * 1000);

      // 코드 생성 후 노드 목록 갱신 (페어링 완료 시 바로 표시)
      setTimeout(fetchNodes, 2000);
    } catch (err: any) {
      onError?.(err.message || 'Failed to create pairing code');
    } finally {
      setLoading(false);
    }
  };

  // 명령 전송: 로컬 폴더 스캔
  const sendIngestCommand = async (nodeId: string, folder: string, extensions: string) => {
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'x-org-id': orgId,
        'x-project-id': projectId,
      };
      if (apiKey) {
        headers['x-api-key'] = apiKey;
      }

      const body: NodeCommandRequest = {
        node_id: nodeId,
        command_type: 'local.folder.ingest',
        params: { folder, extensions },
      };

      const res = await fetch(`${baseUrl}/node/command`, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw new Error(`Failed to send command: ${res.status}`);
      }

      // 명령 전송 성공 (202 Accepted)
      // SSE로 진행 상황 수신
    } catch (err: any) {
      onError?.(err.message || 'Failed to send command');
    }
  };

  // 초기 로드
  useEffect(() => {
    fetchNodes();
  }, [orgId, projectId]);

  // 상태 아이콘
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return '🟢';
      case 'offline':
        return '⚫';
      case 'enrolled':
        return '🔵';
      case 'error':
        return '🔴';
      default:
        return '⚪';
    }
  };

  return (
    <div className="nodesManager">
      <div className="nodesHeader">
        <h2>
          <i className="fas fa-server"></i> Windows Nodes
        </h2>
        <div className="nodeActions">
          <button onClick={fetchNodes} disabled={loading} className="btn-secondary">
            <i className="fas fa-sync-alt"></i> 새로고침
          </button>
          <button onClick={createPairingCode} disabled={loading} className="btn-primary">
            <i className="fas fa-plus"></i> 새 노드 추가
          </button>
        </div>
      </div>

      {/* 페어링 코드 표시 */}
      {pairingCode && (
        <div className="pairingCodeBox">
          <h3>
            <i className="fas fa-qrcode"></i> 페어링 코드
          </h3>
          <div className="pairingCode">{pairingCode}</div>
          <p className="pairingInstructions">
            Windows Node에서 다음 명령을 실행하세요:
          </p>
          <pre className="pairingCommand">node_agent.exe --enroll {pairingCode}</pre>
          <p className="pairingExpiry">
            {pairingExpiry && (
              <>
                유효 시간: {Math.floor((pairingExpiry - Date.now()) / 1000)}초
              </>
            )}
          </p>
        </div>
      )}

      {/* 노드 목록 */}
      <div className="nodesList">
        {loading && nodes.length === 0 && <p>로딩 중...</p>}
        {!loading && nodes.length === 0 && <p className="emptyState">등록된 노드가 없습니다.</p>}

        {nodes.map((node) => (
          <div key={node.node_id} className="nodeCard">
            <div className="nodeCardHeader">
              <div className="nodeStatus">
                {getStatusIcon(node.status)} <strong>{node.node_id}</strong>
              </div>
              <div className="nodeConnection">
                {node.connection_type && (
                  <span className="badge">{node.connection_type.toUpperCase()}</span>
                )}
              </div>
            </div>

            <div className="nodeCardBody">
              <div className="nodeInfo">
                <div className="infoRow">
                  <span className="infoLabel">Hostname:</span>
                  <span className="infoValue">{node.info?.hostname || 'N/A'}</span>
                </div>
                <div className="infoRow">
                  <span className="infoLabel">OS:</span>
                  <span className="infoValue">{node.info?.os_version || 'N/A'}</span>
                </div>
                <div className="infoRow">
                  <span className="infoLabel">Agent:</span>
                  <span className="infoValue">{node.info?.agent_version || 'N/A'}</span>
                </div>
                {node.last_seen && (
                  <div className="infoRow">
                    <span className="infoLabel">Last Seen:</span>
                    <span className="infoValue">{new Date(node.last_seen).toLocaleString('ko-KR')}</span>
                  </div>
                )}
              </div>

              {/* 명령 버튼 (온라인 노드만) */}
              {node.status === 'online' && (
                <div className="nodeActions">
                  <button
                    onClick={() => {
                      const folder = prompt('스캔할 폴더 경로 입력:', 'C:\\Documents');
                      if (folder) {
                        sendIngestCommand(node.node_id, folder, 'pdf,docx,txt');
                      }
                    }}
                    className="btn-secondary btn-sm"
                  >
                    <i className="fas fa-folder-open"></i> 로컬 폴더 스캔
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
