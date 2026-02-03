export async function postJSON<T>(url: string, body: any, headers: Record<string,string>) : Promise<{status:number, json:T | null}> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json', ...headers },
    body: JSON.stringify(body)
  })
  let j: any = null
  try { j = await res.json() } catch {}
  return { status: res.status, json: j as T }
}
