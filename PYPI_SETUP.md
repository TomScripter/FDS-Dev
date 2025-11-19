# PyPI 자동 배포 설정 가이드

## 개요

FDS-Dev는 GitHub Actions를 통해 PyPI에 자동으로 배포됩니다. 태그를 생성하면 자동으로 빌드, 테스트, 배포가 진행됩니다.

---

## 사전 준비

### 1. PyPI 계정 생성

1. https://pypi.org 에서 계정 생성
2. 이메일 인증 완료
3. 2FA (Two-Factor Authentication) 설정 권장

### 2. PyPI API 토큰 생성

1. PyPI 로그인 후 Account Settings 이동
2. API tokens 섹션에서 "Add API token" 클릭
3. Token name: `fds-dev-github-actions`
4. Scope: `Entire account` (첫 배포) 또는 `Project: fds-dev` (이후)
5. 토큰 복사 (한 번만 표시됨!)

**토큰 형식**: `pypi-AgEIcHlwaS5vcmc...` (매우 긴 문자열)

---

## GitHub 설정

### 1. GitHub Secrets 등록

**Repository → Settings → Secrets and variables → Actions**

**Secret 추가**:
- Name: `PYPI_API_TOKEN`
- Value: [PyPI에서 복사한 토큰 전체]

### 2. GitHub Environment 생성 (권장)

**Repository → Settings → Environments → New environment**

**Environment 설정**:
- Name: `pypi`
- Protection rules (선택사항):
  - ✓ Required reviewers (배포 전 승인 필요)
  - ✓ Wait timer (배포 대기 시간)
- Environment secrets:
  - Name: `PYPI_API_TOKEN`
  - Value: [PyPI 토큰]

**장점**:
- 배포 전 수동 승인 가능
- 프로덕션 배포 보호
- 배포 히스토리 추적

---

## 워크플로우 설명

### CI/CD Pipeline (`.github/workflows/ci.yml`)

**트리거**:
- `push` to `main` or `develop` 브랜치
- `pull_request` to `main` 브랜치

**작업**:
1. **테스트** (Python 3.9, 3.10, 3.11, 3.12)
   - 의존성 설치
   - 린터 실행 (flake8)
   - 테스트 실행 (pytest + coverage)
   - Coverage 업로드 (Codecov)

2. **빌드**
   - 패키지 빌드 (`python -m build`)
   - 패키지 검증 (`twine check`)
   - 아티팩트 업로드

**배지 상태**: 자동 업데이트

### PyPI Release (`.github/workflows/release.yml`)

**트리거**:
- `push` with tag `v*` (예: `v0.2.0`, `v1.0.0`)

**작업**:
1. **빌드**
   - 소스 배포판 (`.tar.gz`)
   - 휠 배포판 (`.whl`)

2. **PyPI 배포**
   - Environment: `pypi`
   - Trusted Publisher 사용 (OIDC)
   - `PYPI_API_TOKEN` 사용

3. **GitHub Release**
   - Release 노트 자동 생성
   - 배포 파일 첨부
   - CHANGELOG 링크

---

## 배포 프로세스

### 1. 버전 업데이트

**pyproject.toml** 수정:
```toml
[project]
name = "fds-dev"
version = "0.2.0"  # <- 버전 업데이트
```

### 2. 변경사항 커밋

```bash
git add pyproject.toml
git commit -m "chore: Bump version to 0.2.0"
git push origin main
```

### 3. 태그 생성 및 푸시

```bash
# 태그 생성 (v 접두사 필수)
git tag v0.2.0

# 또는 태그에 메시지 추가
git tag -a v0.2.0 -m "Release v0.2.0: Add comprehensive i18n tests and Korean documentation"

# 태그 푸시
git push origin v0.2.0
```

### 4. 자동 배포 진행

**GitHub Actions 자동 실행**:
1. ✓ 빌드 (Python 3.11)
2. ✓ PyPI 업로드 (environment: pypi)
3. ✓ GitHub Release 생성

**확인**:
- GitHub Actions: https://github.com/flamehaven01/FDS-Dev/actions
- PyPI: https://pypi.org/project/fds-dev/
- GitHub Releases: https://github.com/flamehaven01/FDS-Dev/releases

### 5. 배포 확인

```bash
# 최신 버전 설치 테스트
pip install --upgrade fds-dev

# 버전 확인
fds --version
```

---

## Trusted Publisher 설정 (권장)

PyPI는 GitHub Actions에서 API 토큰 없이 배포할 수 있는 Trusted Publisher를 지원합니다.

### 설정 방법

1. **PyPI 프로젝트 페이지** 이동
   - https://pypi.org/manage/project/fds-dev/settings/publishing/

2. **Add a new publisher** 클릭

3. **GitHub Actions 정보 입력**:
   - Owner: `flamehaven01`
   - Repository name: `FDS-Dev`
   - Workflow name: `release.yml`
   - Environment name: `pypi` (선택사항)

4. **Add** 클릭

### 워크플로우 수정 (Trusted Publisher 사용 시)

`.github/workflows/release.yml`의 `publish-to-pypi` job:

```yaml
publish-to-pypi:
  name: Publish to PyPI
  needs: build
  runs-on: ubuntu-latest
  environment:
    name: pypi
    url: https://pypi.org/p/fds-dev
  permissions:
    id-token: write  # OIDC 사용을 위해 필수

  steps:
  - name: Download distribution packages
    uses: actions/download-artifact@v4
    with:
      name: python-package-distributions
      path: dist/

  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    # password 제거 (Trusted Publisher가 자동 처리)
```

**장점**:
- API 토큰 불필요
- 자동 인증 (OIDC)
- 보안 강화

---

## 버전 관리 규칙

### Semantic Versioning (SemVer)

**형식**: `MAJOR.MINOR.PATCH`

**예시**:
- `v1.0.0` - Major release (호환성 깨지는 변경)
- `v0.2.0` - Minor release (새 기능 추가, 하위 호환)
- `v0.1.1` - Patch release (버그 수정)

**Pre-release**:
- `v0.2.0-alpha.1` - 알파 버전
- `v0.2.0-beta.1` - 베타 버전
- `v0.2.0-rc.1` - Release Candidate

### 태그 규칙

**필수**:
- ✓ `v` 접두사 사용 (`v0.2.0`)
- ✓ SemVer 형식 준수
- ✓ pyproject.toml 버전과 일치

**권장**:
- 태그에 release 노트 추가 (`-a` 옵션)
- 주요 변경사항 요약

---

## 문제 해결

### 배포 실패: Authentication error

**원인**: PyPI API 토큰 오류

**해결**:
1. GitHub Secrets의 `PYPI_API_TOKEN` 확인
2. PyPI에서 토큰 재생성
3. GitHub Secrets 업데이트

### 배포 실패: File already exists

**원인**: 같은 버전이 이미 PyPI에 존재

**해결**:
1. pyproject.toml의 버전 증가
2. 새 태그 생성
3. 재배포

**참고**: PyPI는 같은 버전을 다시 업로드할 수 없습니다.

### 배포 실패: Invalid distribution

**원인**: 패키지 구조 오류

**해결**:
```bash
# 로컬에서 빌드 테스트
python -m build

# 패키지 검증
twine check dist/*

# 테스트 PyPI에 먼저 배포
twine upload --repository testpypi dist/*
```

### CI 테스트 실패

**원인**: 의존성 또는 테스트 오류

**해결**:
1. 로컬에서 테스트 실행
   ```bash
   pytest tests/ -v
   ```
2. 의존성 확인
   ```bash
   pip install -e .
   ```
3. 수정 후 재푸시

---

## 체크리스트

### 첫 배포 전

- [ ] PyPI 계정 생성 및 이메일 인증
- [ ] PyPI API 토큰 생성
- [ ] GitHub Secrets에 `PYPI_API_TOKEN` 등록
- [ ] GitHub Environment `pypi` 생성 (선택)
- [ ] pyproject.toml 버전 확인
- [ ] 로컬 빌드 테스트 (`python -m build`)
- [ ] 로컬 테스트 통과 (`pytest tests/ -v`)

### 배포 시

- [ ] pyproject.toml 버전 업데이트
- [ ] CHANGELOG.md 업데이트 (선택)
- [ ] 변경사항 커밋 및 푸시
- [ ] 태그 생성 (`git tag v0.2.0`)
- [ ] 태그 푸시 (`git push origin v0.2.0`)
- [ ] GitHub Actions 배포 확인
- [ ] PyPI 배포 확인
- [ ] 설치 테스트 (`pip install --upgrade fds-dev`)

---

## 참고 자료

**GitHub Actions**:
- https://docs.github.com/en/actions
- https://github.com/pypa/gh-action-pypi-publish

**PyPI**:
- https://pypi.org/help/
- https://packaging.python.org/

**Trusted Publishers**:
- https://docs.pypi.org/trusted-publishers/

**Semantic Versioning**:
- https://semver.org/

---

**마지막 업데이트**: 2025-11-19
**FDS-Dev 버전**: 0.2.0 (예정)
