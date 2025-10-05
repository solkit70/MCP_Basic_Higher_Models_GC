# 공개 MCP 서버 비교 (M1)

[검증]
- 공식 레퍼런스 서버 리포지토리: https://github.com/modelcontextprotocol/servers — 확인일: 2025-10-05
- 조직 개요/SDK 목록: https://github.com/modelcontextprotocol — 확인일: 2025-10-05
- 프로토콜 사양 버전: https://spec.modelcontextprotocol.io/ (현재 2025-06-18 표기) — 확인일: 2025-10-05

비교 대상(레퍼런스)
- Filesystem: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem
- Git: https://github.com/modelcontextprotocol/servers/tree/main/src/git
- Fetch: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch

선정 이유
- 학습용으로 범용성 높고(파일, 깃, 웹콘텐츠) 실습 환경에서 바로 체감 가능.
- 공식 레포에 포함된 표준 예시로 유지보수/호환성 측면에서 안전한 출발점.

비교표
| 항목 | Filesystem | Git | Fetch |
|---|---|---|---|
| 핵심 기능(툴) | 파일 읽기/쓰기/나열, 경로 접근 제어 | 리포지토리 탐색/검색/조회 등 | URL 가져오기/변환(HTML→텍스트/MD 등) |
| 리소스 | 디렉터리/파일 컨텐츠 노출 | 커밋/파일/로그 등 메타데이터 | 페치 결과(정규화된 콘텐츠) |
| 전송 방식 | STDIO(기본), 일부 환경에서 Streamable HTTP(SSE)도 호환 | STDIO(uvx/pip 기반 실행), SSE 클라이언트와도 호환 가능 | STDIO(기본), SSE 호환 |
| 인증/키 | 기본 없음(로컬 접근 제어 중심) | 일반적으로 없음(프라이빗 저장소 연동 시 별도 자격 필요) | 공개 웹은 무관, 사설 소스는 별도 키 필요 |
| 라이선스 | MIT (레포 전반) | MIT | MIT |
| 유지보수 상태 | 공식 레포 내 활성 | 공식 레포 내 활성 | 공식 레포 내 활성 |

시작 방법(예)
- Filesystem (Node): `npx -y @modelcontextprotocol/server-filesystem <허용_루트_경로>`
- Git (Python): `uvx mcp-server-git --repository <path/to/repo>`
- Fetch (Node): 레포 내 `src/fetch` 서버를 npx로 실행하거나 로컬 빌드 후 명령 전달

적용 시 주의
- 파일/깃 서버는 로컬 권한·경로 스코프를 엄격히 제한하십시오(.mcpignore 유사 접근 통제 고려).
- 네트워크(HTTP) 기반 서버는 레이트리밋·리다이렉트·콘텐츠 정제 정책을 명시.
- SSE 사용 시 클라이언트 호환성과 프록시/방화벽 통과 여부 확인.

대안/확장 후보
- Everything, Memory 등 다른 레퍼런스 서버로 확장 학습 가능
- Third-Party 서버(예: GitHub, Vercel, Netlify 등)로 실전 통합 연습

사실성 메모
- 각 서버의 세부 툴/리소스는 버전에 따라 달라질 수 있으므로, 실습 전 README와 예제 커맨드를 최신으로 재확인하십시오.
