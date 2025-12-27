# 認証フロー詳細ドキュメント

## 概要

本アプリケーションでは Google OAuth 2.0 を使用した認証システムを実装しています。フロントエンド（Next.js）とバックエンド（FastAPI）を連携させ、シームレスな認証体験を提供します。

## アーキテクチャ

```
[フロントエンド] ←→ [バックエンド] ←→ [Google OAuth]
   Next.js           FastAPI         Google APIs
```

## 認証フロー詳細

### 1. ログイン開始

**フロントエンド**: `apps/web/src/contexts/auth-context.tsx`

```typescript
const login = () => {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
  window.location.href = `${apiBaseUrl}/auth/login`
}
```

**処理内容**:
- ユーザーがログインボタンをクリック
- バックエンドの `/api/v1/auth/login` エンドポイントにリダイレクト（Google OAuth設定はバックエンド側の `.env` に集約）

### 2. バックエンド認証開始

**バックエンド**: `apps/api/app/routers/auth/auth.py`

```python
@router.get("/login")
async def login(
    request: Request,
    client_id: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    response_type: str = "code",
    scope: str = "openid profile email"
):
    if settings.DEBUG:
        # モック認証（開発用）
        state = secrets.token_urlsafe(32)
        mock_code = f"mock_auth_code_{secrets.token_urlsafe(16)}"
        target_redirect = redirect_uri or f"{settings.FRONTEND_BASE_URL}/callback"
        redirect_url = f"{target_redirect}?code={mock_code}&state={state}"
        return RedirectResponse(url=redirect_url)
    
    # 本番認証（Google OAuth）
    authorization_url = "https://accounts.google.com/o/oauth2/v2/auth"
    state = secrets.token_urlsafe(32)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": response_type,
        "scope": scope,
        "state": state,
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = urlencode(params)
    redirect_url = f"{authorization_url}?{query_string}"
    return RedirectResponse(url=redirect_url)
```

**処理内容**:
- 開発環境（`DEBUG=true`）の場合：モック認証コードを生成してフロントエンドにリダイレクト
- 本番環境の場合：Google の認証画面にリダイレクト
- セキュリティのため `state` パラメータを生成

### 3. Google 認証画面

**Google OAuth 2.0 フロー**:
- ユーザーが Google の認証画面でログイン
- アプリケーションの権限を承認
- Google が認可コード（authorization code）を生成

### 4. Google コールバック

**バックエンド**: `apps/api/app/routers/auth/auth.py`

```python
@router.get("/google/callback")
async def google_callback(
    code: str = Query(...),
    state: Optional[str] = None,
):
    """Forward Google callback to frontend callback page"""
    target = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/callback"
    params = {"code": code}
    if state:
        params["state"] = state
    redirect_url = f"{target}?{urlencode(params)}"
    return RedirectResponse(url=redirect_url)
```

**処理内容**:
- Google から認可コードを受け取る
- フロントエンドの `/callback` ページにリダイレクト
- 認可コードをクエリパラメータとして渡す

### 5. フロントエンドコールバック処理

**フロントエンド**: `apps/web/src/app/callback/page.tsx`

```typescript
const handleCallback = async () => {
  try {
    const code = searchParams.get('code')
    const authError = searchParams.get('error')
    
    if (authError) {
      setError(`認証エラー: ${authError}`)
      return
    }
    
    if (!code) {
      setError('認証コードが取得できませんでした')
      return
    }
    
    // バックエンドに認可コードを送信
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
    const response = await fetch(`${apiBaseUrl}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    })
    
    if (!response.ok) {
      throw new Error('認証に失敗しました')
    }
    
    const data = await response.json()
    
    // 認証情報を保存
    setAuthData(data.access_token, data.user)
    
    // ホームページにリダイレクト
    router.push('/')
  } catch (err) {
    console.error('Callback error:', err)
    setError(err.message)
  }
}
```

**処理内容**:
- URL から認可コードを取得
- バックエンドの `/api/v1/auth/token` エンドポイントに POST リクエスト
- レスポンスからトークンとユーザー情報を取得
- `setAuthData` で認証状態を更新
- ホームページにリダイレクト

### 6. トークン交換

**バックエンド**: `apps/api/app/routers/auth/auth.py`

```python
@router.post("/token")
async def exchange_token(
    request: Request,
    db: Session = Depends(get_db)
):
    body = await request.json()
    code = body.get("code")
    
    if settings.DEBUG or code.startswith("mock_auth_code_"):
        # モック認証処理
        mock_user_data = {
            "sub": "mock_user_123",
            "name": "Test User",
            "email": "test@example.com",
            "picture": "https://via.placeholder.com/150",
        }
        
        user = db.query(User).filter(User.sub == mock_user_data["sub"]).first()
        if not user:
            user = User(
                sub=mock_user_data["sub"],
                name=mock_user_data["name"],
                email=mock_user_data["email"],
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        mock_token = f"mock_jwt_token_{secrets.token_urlsafe(32)}"
        return {
            "access_token": mock_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "picture": mock_user_data["picture"],
            },
        }
    
    # 本番認証処理（Google OAuth）
    token_endpoint = "https://oauth2.googleapis.com/token"
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            token_endpoint,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15.0,
        )
    
    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to exchange authorization code with Google",
        )
    
    token_data = token_response.json()
    access_token = token_data.get("access_token")
    
    # Google からユーザー情報を取得
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"
    async with httpx.AsyncClient() as client:
        userinfo_response = await client.get(
            userinfo_endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15.0,
        )
    
    profile = userinfo_response.json()
    sub = profile.get("id")
    
    # データベースにユーザーを保存または取得
    user = db.query(User).filter(User.sub == sub).first()
    if not user:
        user = User(
            sub=sub,
            name=profile.get("name") or profile.get("given_name") or "Google User",
            email=profile.get("email") or "",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "access_token": access_token,
        "refresh_token": token_data.get("refresh_token"),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
        "id_token": token_data.get("id_token"),
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "picture": profile.get("picture"),
        },
    }
```

**処理内容**:
- モック認証の場合：モックユーザーを作成/取得し、モックトークンを返す
- 本番認証の場合：
  1. Google のトークンエンドポイントに認可コードを送信
  2. アクセストークンとリフレッシュトークンを取得
  3. Google のユーザー情報エンドポイントからプロフィール情報を取得
  4. データベースにユーザーを保存または取得
  5. トークンとユーザー情報をフロントエンドに返す

### 7. 認証状態管理

**フロントエンド**: `apps/web/src/contexts/auth-context.tsx`

```typescript
const setAuthData = (accessToken: string, authUser: User) => {
  setToken(accessToken)
  setUser(authUser)
  localStorage.setItem('access_token', accessToken)
  localStorage.setItem('user', JSON.stringify(authUser))
  setIsLoading(false)
}

const isAuthenticated = !!user && !!token
```

**処理内容**:
- トークンとユーザー情報を React state に保存
- localStorage にも永続化
- `isLoading` を `false` に設定して認証完了を通知

### 8. 認証ガード

**フロントエンド**: `apps/web/src/components/auth/auth-guard.tsx`

```typescript
export function AuthGuard({ 
  children, 
  redirectTo = '/login', 
  requireAuth = true 
}: AuthGuardProps): JSX.Element {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (isLoading) return

    if (requireAuth && !isAuthenticated) {
      router.push(redirectTo)
    } else if (!requireAuth && isAuthenticated) {
      router.push('/')
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, router])

  // ローディング中は何も表示しない
  if (isLoading) {
    return <LoadingSpinner />
  }

  // 認証状態に応じて表示を制御
  if (requireAuth && !isAuthenticated) {
    return <UnauthorizedMessage />
  }

  if (!requireAuth && isAuthenticated) {
    return <RedirectMessage />
  }

  return <>{children}</>
}
```

**処理内容**:
- ページの認証要件に応じてアクセス制御
- ローディング中は適切な UI を表示
- 認証状態に応じてリダイレクト

## ログアウトフロー

### 1. ログアウト開始

**フロントエンド**: `apps/web/src/contexts/auth-context.tsx`

```typescript
const logout = () => {
  // 認証情報をクリア
  setUser(null)
  setToken(null)
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  setIsLoading(false)
  
  // バックエンドのログアウトエンドポイントにリダイレクト
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
  const returnTo = encodeURIComponent(window.location.origin)
  
  window.location.href = `${apiBaseUrl}/auth/logout?client_id=${clientId}&return_to=${returnTo}`
}
```

### 2. バックエンドログアウト処理

**バックエンド**: `apps/api/app/routers/auth/auth.py`

```python
@router.get("/logout")
async def logout(
    request: Request,
    client_id: Optional[str] = None,
    return_to: Optional[str] = None,
):
    target = return_to or f"{settings.FRONTEND_BASE_URL.rstrip('/')}/login"
    
    response = RedirectResponse(url=target)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("session")
    
    return response
```

**処理内容**:
- 指定された URL（通常はログインページ）にリダイレクト
- 関連するクッキーを削除

## 環境設定

### フロントエンド環境変数

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_BASE_URL=http://localhost:3000
```

### バックエンド環境変数

```bash
DEBUG=false
GOOGLE_CLIENT_ID=your-google-oauth-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
FRONTEND_BASE_URL=http://localhost:3000
```

### Google Cloud Console 設定

**Authorized redirect URIs**:
```
http://localhost:8000/api/v1/auth/google/callback
```

## セキュリティ考慮事項

1. **State パラメータ**: CSRF 攻撃を防ぐため、認証フローで state パラメータを使用
2. **HTTPS**: 本番環境では必ず HTTPS を使用
3. **トークン管理**: アクセストークンは適切に期限管理
4. **リフレッシュトークン**: 必要に応じてリフレッシュトークンを使用
5. **環境変数**: 機密情報は環境変数で管理

## エラーハンドリング

### よくあるエラー

1. **`redirect_uri_mismatch`**: Google Cloud Console の設定と実際のリダイレクト URI が一致しない
2. **`invalid_grant`**: 認可コードが無効または期限切れ
3. **`access_denied`**: ユーザーが認証を拒否

### エラー対応

- フロントエンドでエラー状態を適切に表示
- バックエンドで適切な HTTP ステータスコードを返す
- ログを記録してデバッグを支援

## 開発・テスト

### モック認証

開発時は `DEBUG=true` に設定することで、Google 認証をスキップしてモックユーザーでログインできます。

### テスト手順

1. フロントエンドとバックエンドを起動
2. ログインボタンをクリック
3. Google 認証画面でログイン
4. ホームページにリダイレクトされることを確認
5. ログアウト機能をテスト

## 今後の改善点

1. **リフレッシュトークン**: アクセストークンの自動更新
2. **セッション管理**: より堅牢なセッション管理
3. **多要素認証**: セキュリティの向上
4. **SSO**: 他の認証プロバイダーとの連携
