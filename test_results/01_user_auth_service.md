# Verification Test Log: User & Auth Service

- **Execution Timestamp**: 2026-09-20T08:23:17.589775+00:00
- **Tests Executed**: 6
- **Passed**: 6 / 6 (100.0%)
- **Average Latency**: `9.04 ms`

---

## Individual Test Executions & Payloads

### [TEST-AUTH-01] Student Registration (POST /api/v1/auth/register)
- **Verdict**: ✅ PASS
- **Status Code**: `201`
- **Response Time**: `52.29 ms`
- **Endpoint**: `POST /api/v1/auth/register`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "student_98267a@veritas.edu.ng", "password": "SecurePassword2026!", "first_name": "Emeka", "last_name": "Adeleke", "institution_id": "inst_veritas", "role": "student"}'
```

#### Payload Package Sent
```json
{
  "email": "student_98267a@veritas.edu.ng",
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
    "id": "usr_test_5db8020a",
    "email": "student_98267a@veritas.edu.ng",
    "first_name": "Emeka",
    "last_name": "Adeleke",
    "role": "student",
    "institution_id": "inst_veritas",
    "is_verified": false,
    "created_at": "2026-09-20T08:23:04.867735+00:00"
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
- **Response Time**: `0.03 ms`
- **Endpoint**: `POST /api/v1/auth/verify-email`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token": "vtok_b7af01d47f4740ce9b7c231929f551bf"}'
```

#### Payload Package Sent
```json
{
  "token": "vtok_b7af01d47f4740ce9b7c231929f551bf"
}
```

#### Response Package Received
```json
{
  "status": "success",
  "message": "Email verified successfully",
  "data": {
    "user_id": "usr_test_5db8020a",
    "email": "student_98267a@veritas.edu.ng",
    "is_verified": true
  }
}
```

---

### [TEST-AUTH-04] RS256 JWT Login & Token Generation (POST /api/v1/auth/login)
- **Verdict**: ✅ PASS
- **Status Code**: `200`
- **Response Time**: `1.87 ms`
- **Endpoint**: `POST /api/v1/auth/login`

#### Equivalent cURL Request
```bash
curl -X POST "http://localhost:8080/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "student_98267a@veritas.edu.ng", "password": "SecurePassword2026!"}'
```

#### Payload Package Sent
```json
{
  "email": "student_98267a@veritas.edu.ng",
  "password": "SecurePassword2026!"
}
```

#### Response Package Received
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfdGVzdF81ZGI4MDIwYSIsImVtYWlsIjoic3R1ZGVudF85ODI2N2FAdmVyaXRhcy5lZHUubmciLCJpbnN0aXR1dGlvbl9pZCI6Imluc3RfdmVyaXRhcyIsInJvbGUiOiJzdHVkZW50IiwiaWF0IjoxNzg5ODkyNTg0LCJleHAiOjE3ODk4OTM0ODQsImlzcyI6Inp1cmktdXNlci1zZXJ2aWNlIn0.CQdYFp8VHHasdL2ETw3cARJrrroXD1_4ADPS7PsL5OPFQCoFbJgg2nRch99lC7E_K90-imJei8_V6YlrRHmdrxujvZte4bpGBaFqN79AR6lufVUc-sUCMCR2WDt4dOR7oU1Ea1ItSPhSbWIBb0gXr--UhRolud7msSGcOFfK02N4dUzkFoA4wxL8Eulz0a7bGoBDaOB6Cm_roriOiN8zWxXdRmQahT5WB7WlFqUUiQ3SawOOMkbzTxTQDtk1kS_J0Q8fPxjzBDOB5K03NL8WNDoVUNZDv_Ex75rqbZTqcGX-QJnQ5TeneaBuEu_cRfUZS8dCAJP5sAVr-MaUKRp1Ug",
    "refresh_token": "rft_68bdc563c7ec47a1bb9bc00d144e47dc",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_test_5db8020a",
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
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfdGVzdF81ZGI4MDIwYSIsImVtYWlsIjoic3R1ZGVudF85ODI2N2FAdmVyaXRhcy5lZHUubmciLCJpbnN0aXR1dGlvbl9pZCI6Imluc3RfdmVyaXRhcyIsInJvbGUiOiJzdHVkZW50IiwiaWF0IjoxNzg5ODkyNTg0LCJleHAiOjE3ODk4OTM0ODQsImlzcyI6Inp1cmktdXNlci1zZXJ2aWNlIn0.CQdYFp8VHHasdL2ETw3cARJrrroXD1_4ADPS7PsL5OPFQCoFbJgg2nRch99lC7E_K90-imJei8_V6YlrRHmdrxujvZte4bpGBaFqN79AR6lufVUc-sUCMCR2WDt4dOR7oU1Ea1ItSPhSbWIBb0gXr--UhRolud7msSGcOFfK02N4dUzkFoA4wxL8Eulz0a7bGoBDaOB6Cm_roriOiN8zWxXdRmQahT5WB7WlFqUUiQ3SawOOMkbzTxTQDtk1kS_J0Q8fPxjzBDOB5K03NL8WNDoVUNZDv_Ex75rqbZTqcGX-QJnQ5TeneaBuEu_cRfUZS8dCAJP5sAVr-MaUKRp1Ug"
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
    "id": "usr_test_5db8020a",
    "email": "student_98267a@veritas.edu.ng",
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
