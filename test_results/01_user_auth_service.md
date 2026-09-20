# Verification Test Log: User & Auth Service

- **Execution Timestamp**: 2026-09-20T15:07:08.218704+00:00
- **Tests Executed**: 6
- **Passed**: 6 / 6 (100.0%)
- **Average Latency**: `9.12 ms`

---

## Individual Test Executions & Payloads

### [TEST-AUTH-01] Student Registration (POST /api/v1/auth/register)
- **Verdict**: ✅ PASS
- **Status Code**: `201`
- **Response Time**: `52.26 ms`
- **Endpoint**: `POST /api/v1/auth/register`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "student_d1c9a9@veritas.edu.ng", "password": "SecurePassword2026!", "first_name": "Emeka", "last_name": "Adeleke", "institution_id": "inst_veritas", "role": "student"}'
```

#### Payload Package Sent
```json
{
  "email": "student_d1c9a9@veritas.edu.ng",
  "password": "SecurePassword2026!",
  "first_name": "Emeka",
  "last_name": "Adeleke",
  "institution_id": "inst_veritas",
  "role": "student"
}
```

#### Response Package Received
```json
{
  "status": "success",
  "code": 201,
  "data": {
    "id": "usr_test_291cd2b7",
    "email": "student_d1c9a9@veritas.edu.ng",
    "first_name": "Emeka",
    "last_name": "Adeleke",
    "role": "student",
    "institution_id": "inst_veritas",
    "is_verified": false,
    "created_at": "2026-09-20T15:06:53.713870+00:00"
  }
}
```

---

### [TEST-AUTH-02] Public Key Retrieval (GET /api/v1/auth/public-key)
- **Verdict**: ✅ PASS
- **Status Code**: `200`
- **Response Time**: `0.01 ms`
- **Endpoint**: `GET /api/v1/auth/public-key`

#### Equivalent cURL Request
```bash
curl -X GET "http://localhost:8080/api/v1/auth/public-key" \
  -H "Accept: application/json"
```

#### Payload Package Sent
```json
{}
```

#### Response Package Received
```json
{
  "status": "success",
  "data": {
    "algorithm": "RS256",
    "key_type": "RSA-2048",
    "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBC...\n-----END PUBLIC KEY-----"
  }
}
```

---

### [TEST-AUTH-03] Email Verification Token (POST /api/v1/auth/verify-email)
- **Verdict**: ✅ PASS
- **Status Code**: `200`
- **Response Time**: `0.37 ms`
- **Endpoint**: `POST /api/v1/auth/verify-email`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token": "vtok_a483d07f7d1a49eabbf403f838027628"}'
```

#### Payload Package Sent
```json
{
  "token": "vtok_a483d07f7d1a49eabbf403f838027628"
}
```

#### Response Package Received
```json
{
  "status": "success",
  "message": "Email verified successfully",
  "data": {
    "user_id": "usr_test_291cd2b7",
    "email": "student_d1c9a9@veritas.edu.ng",
    "is_verified": true
  }
}
```

---

### [TEST-AUTH-04] RS256 JWT Login & Token Generation (POST /api/v1/auth/login)
- **Verdict**: ✅ PASS
- **Status Code**: `200`
- **Response Time**: `2.08 ms`
- **Endpoint**: `POST /api/v1/auth/login`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "student_d1c9a9@veritas.edu.ng", "password": "SecurePassword2026!"}'
```

#### Payload Package Sent
```json
{
  "email": "student_d1c9a9@veritas.edu.ng",
  "password": "SecurePassword2026!"
}
```

#### Response Package Received
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfdGVzdF8yOTFjZDJiNyIsImVtYWlsIjoic3R1ZGVudF9kMWM5YTlAdmVyaXRhcy5lZHUubmciLCJpbnN0aXR1dGlvbl9pZCI6Imluc3RfdmVyaXRhcyIsInJvbGUiOiJzdHVkZW50IiwiaWF0IjoxNzg5OTE2ODEzLCJleHAiOjE3ODk5MTc3MTMsImlzcyI6Inp1cmktdXNlci1zZXJ2aWNlIn0.ZISet--6QI8W_CnJZgNbnPom1B17FfE7wP5N-6IJvCwlALfeb5JmSI0ON_jwnFAEAQnTjQdDF8XUkgLBNkDlIDvz_h1coQnQD_iNvDPvC_20Yg_SzWbun-6rzZvWZfSSYMjk2tS8Ue8tMjUMwsies8DPaqjjIujF1lhcDWbWSkqX9RMJnyNxCvZjEAMcFW0FkviL4-gAabCAgbDvu6sZ7hV2BcNw8VKMzqQf2CB-HnsXtk7kxXsUPsNt0Rid7BWKXzxh78sgwo26PrN47pcvGUp8v0Z5ClGmQ3hsFY4wCqGhIUOUzmLJFMAJXOD7iMg9S8AggOnPkItQH_tx-IfurA",
    "refresh_token": "rft_24012b16cb724c24aabc2da501e04074",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_test_291cd2b7",
      "role": "student",
      "institution_id": "inst_veritas"
    }
  }
}
```

---

### [TEST-AUTH-05] Authenticated Profile Inspection (GET /api/v1/users/me)
- **Verdict**: ✅ PASS
- **Status Code**: `200`
- **Response Time**: `0.01 ms`
- **Endpoint**: `GET /api/v1/users/me`

#### Equivalent cURL Request
```bash
curl -X GET "http://localhost:8080/api/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfdGVzdF8yOTFjZDJiNyIsImVtYWlsIjoic3R1ZGVudF9kMWM5YTlAdmVyaXRhcy5lZHUubmciLCJpbnN0aXR1dGlvbl9pZCI6Imluc3RfdmVyaXRhcyIsInJvbGUiOiJzdHVkZW50IiwiaWF0IjoxNzg5OTE2ODEzLCJleHAiOjE3ODk5MTc3MTMsImlzcyI6Inp1cmktdXNlci1zZXJ2aWNlIn0.ZISet--6QI8W_CnJZgNbnPom1B17FfE7wP5N-6IJvCwlALfeb5JmSI0ON_jwnFAEAQnTjQdDF8XUkgLBNkDlIDvz_h1coQnQD_iNvDPvC_20Yg_SzWbun-6rzZvWZfSSYMjk2tS8Ue8tMjUMwsies8DPaqjjIujF1lhcDWbWSkqX9RMJnyNxCvZjEAMcFW0FkviL4-gAabCAgbDvu6sZ7hV2BcNw8VKMzqQf2CB-HnsXtk7kxXsUPsNt0Rid7BWKXzxh78sgwo26PrN47pcvGUp8v0Z5ClGmQ3hsFY4wCqGhIUOUzmLJFMAJXOD7iMg9S8AggOnPkItQH_tx-IfurA"
```

#### Payload Package Sent
```json
{}
```

#### Response Package Received
```json
{
  "status": "success",
  "data": {
    "id": "usr_test_291cd2b7",
    "email": "student_d1c9a9@veritas.edu.ng",
    "first_name": "Emeka",
    "last_name": "Adeleke",
    "role": "student",
    "active_institution_id": "inst_veritas"
  }
}
```

---

### [TEST-AUTH-06] Unauthorized Access Rejection (401 Verification)
- **Verdict**: ✅ PASS
- **Status Code**: `401`
- **Response Time**: `0.0 ms`
- **Endpoint**: `GET /api/v1/users/me`

#### Equivalent cURL Request
```bash
curl -X GET "http://localhost:8080/api/v1/users/me"
```

#### Payload Package Sent
```json
{}
```

#### Response Package Received
```json
{
  "error": "unauthorized",
  "message": "Missing or malformed Authorization header"
}
```

---
