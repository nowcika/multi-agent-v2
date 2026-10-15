# 환경 설정

## 1. Codex와 Python 확인

Codex 설치와 로그인은 [공식 CLI 안내](https://learn.chatgpt.com/docs/codex-cli)를 따릅니다. 설치된 환경에서는 아래를 확인합니다.

```bash
codex --version
python3 --version
```

이 저장소는 별도 서버, MCP 서버, API 키를 요구하지 않습니다. 사용 중인 Codex의 정상적인 인증과 서브에이전트 기능이 필요합니다. Python 3.10 이상은 예제 실행용입니다.

## 2. 스킬 설치 위치

README의 개인 설치는 `$HOME/.agents/skills/multi-agent-v2`를 사용합니다. 특정 프로젝트에만 설치하려면 해당 프로젝트 루트에서 다음을 실행합니다. 첫 경로는 내려받은 저장소의 실제 위치로 바꾸세요.

```bash
mkdir -p .agents/skills
cp -R /path/to/multi-agent-v2/skills/multi-agent-v2 .agents/skills/
```

개인 경로와 프로젝트 경로 양쪽에 중복 설치하면 같은 이름이 두 번 보일 수 있습니다. 한 위치를 선택하는 편이 편리합니다. 과거 환경의 `~/.codex/skills` 경로와 현재 설치 경로를 혼동하지 마세요. [공식 로컬 스킬 경로 안내](https://learn.chatgpt.com/docs/build-skills)를 확인할 수 있습니다.

## 3. 협업 기능 확인

Codex에 다음을 요청합니다.

```text
현재 에이전트 생성과 동료 에이전트에게 직접 메시지 보내기가 가능한지
실제로 노출된 도구를 확인해 줘. 가능한 도구와 제한을 알려 줘.
```

최초 검증 환경에서는 `spawn_agent`, `send_message`, `followup_task`, `list_agents`, `wait_agent`가 제공됐습니다. 이름이 같다는 사실만으로 충분하지는 않습니다. 자식 에이전트도 동료에게 메시지를 보낼 수 있어야 합니다.

현재 공식 문서에 따른 선택적 설정 예시는 다음과 같습니다. 기존 `~/.codex/config.toml`의 `[agents]` 항목에 병합하며, 같은 테이블을 중복 추가하지 마세요.

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 2
```

이 동시 실행 수는 생성된 서브에이전트 기준입니다. 세션·호스트에 더 낮은 한도가 적용되면 그 한도를 따릅니다. 모델은 부모 설정을 사용해 시작할 수 있습니다. 설정을 바꾼 뒤 새 세션에서 도구를 다시 확인하세요. [공식 서브에이전트 설정](https://learn.chatgpt.com/docs/agent-configuration/subagents)을 참고했습니다.

### v2 기능 플래그가 있는 CLI

이 저장소를 준비한 CLI 0.162.1의 `codex features list`에는 `multi_agent_v2`가 있었습니다. 특정 빌드에서 해당 기능을 선택하려면 먼저 자신의 CLI 목록을 확인하세요.

```bash
codex features list
# multi_agent_v2 항목이 있는 빌드에서만:
codex -c features.multi_agent_v2=true
```

이 옵션은 해당 실행에만 전달하며 사용자 설정을 덮어쓰지 않습니다. 이 플래그의 모든 빌드 호환성은 시험하지 않았습니다. 최초 협업 시험은 이 대화에 노출된 도구로 수행했고, 별도 CLI 프로세스의 기능 목록과 실제 대화의 도구 구성이 같다고 가정하지 않았습니다. 플래그가 없어도 필요한 도구가 제공된다면 도구 계약을 기준으로 판단합니다.

## 4. Ubuntu의 bwrap 오류

다음 오류가 명령 실행 전에 발생할 수 있습니다.

```text
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

최초 테스트 호스트에서는 AppArmor 감사 로그에 `bwrap`의 `net_admin`, `setpcap` 거부가 기록되어 있었고, 필요한 프로필이 없었습니다. 같은 오류라도 먼저 원인을 확인해야 합니다. 이 사례에서는 아래 프로필 설치로 해결했습니다.

```bash
sudo apt update
sudo apt install bubblewrap apparmor-profiles apparmor-utils
sudo install -m 0644 \
  /usr/share/apparmor/extra-profiles/bwrap-userns-restrict \
  /etc/apparmor.d/bwrap-userns-restrict
sudo apparmor_parser -r /etc/apparmor.d/bwrap-userns-restrict
```

시스템 관리자가 호스트 터미널에서 실행하는 명령입니다. 적용 후 Codex에서 실패했던 명령을 다시 실행해 확인합니다. 이 프로필 해결 방법은 [OpenAI 공식 샌드박스 문서](https://learn.chatgpt.com/docs/sandboxing#prerequisites)에 안내되어 있습니다.

## 자주 겪는 문제

| 증상 | 확인할 내용 |
| --- | --- |
| 스킬이 보이지 않음 | 설치 경로 아래 `SKILL.md` 존재 여부, `/skills`, 새 세션 |
| 에이전트가 생성되지 않음 | 협업 도구 제공 여부, 상위 지침, 동시 실행 한도 |
| 동료에게 메시지를 못 보냄 | 생성 응답의 실제 식별자·정규 경로, 자식 도구 권한 |
| 완료한 동료가 답하지 않음 | `send_message`만 보냈는지 확인하고 리더가 `followup_task` 사용 |
| 파일 수정이 충돌함 | 파일별 수정 담당과 소유권 이전 합의 여부 |
