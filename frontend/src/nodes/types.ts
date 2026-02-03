/**
 * Windows Node 관련 타입 정의
 */

export interface NodeInfo {
  hostname?: string;
  os_version?: string;
  agent_version?: string;
  [key: string]: any;
}

export interface NodeState {
  node_id: string;
  tenant_id?: string;
  status: 'enrolled' | 'online' | 'offline' | 'error';
  enrolled_at?: string;
  last_seen?: string;
  connection_type?: 'wss' | 'poll' | null;
  info?: NodeInfo;
}

export interface PairingCodeResponse {
  pairing_code: string;
  expires_in: number; // seconds
}

export interface NodeCommandRequest {
  node_id: string;
  command_type: string;
  params?: Record<string, any>;
}

export interface NodeCommandResponse {
  command_id: string;
  node_id: string;
  accepted: boolean;
}

export interface NodeListResponse {
  nodes: NodeState[];
  total: number;
}
