import { apiKey } from '@/lib/youcam';
export async function GET() {
  return Response.json({configured:Boolean(await apiKey())},{headers:{'Cache-Control':'no-store'}});
}
