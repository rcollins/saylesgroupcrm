# Resolving Vercel NOT_FOUND (404) for Django

## 1. The fix (what to change)

**Done in this repo:**

- **`vercel.json`**  
  - Use the **`@ardnt/vercel-python-wsgi`** builder (not `@vercel/python`) so that your Django WSGI app is actually invoked for every request.  
  - Route destination should be **`/index.py`** (leading slash so Vercel resolves the serverless function correctly).

- **Root Directory in Vercel**  
  In the Vercel project: **Settings → General → Root Directory** must be the folder that contains `manage.py`, `index.py`, `vercel.json`, and `package.json` (e.g. `recrmapp` if your repo root is one level above).

- **Dependencies**  
  `package.json` must include `@ardnt/vercel-python-wsgi` so the build can run the WSGI builder.  
  `requirements.txt` must be in that same root folder so the builder can install Python deps.

**Checklist:**

1. `vercel.json` uses `"use": "@ardnt/vercel-python-wsgi"` and `"dest": "/index.py"`.
2. Root Directory in Vercel points at the directory that has `index.py` and `vercel.json`.
3. Build runs successfully (no red build in the dashboard).
4. Env vars (e.g. `SECRET_KEY`, `DATABASE_URL`) are set in Vercel.

---

## 2. Root cause (why the error happened)

**What the code was doing vs what it needed to do**

- **What it was doing:**  
  `vercel.json` was using **`@vercel/python`** with `index.py`.  
  The generic Python runtime only runs a **request handler**: a function or callable it can call with one request and expect a response. It does **not** start a WSGI server or call a WSGI app.

- **What it needed to do:**  
  Django is a **WSGI application**. Something must:
  - Receive the HTTP request from Vercel.
  - Convert it into a WSGI `environ` and `start_response` call.
  - Call your Django app (e.g. `application(environ, start_response)`).
  - Convert the WSGI response back into the HTTP response Vercel returns.

**What actually triggered NOT_FOUND**

- With `@vercel/python`, the runtime looked for a **handler** in `index.py` (e.g. a default export or a specific handler signature). Your file only exposed a WSGI callable (`app` / `application`), which is not that handler.
- So either:
  - No valid serverless function was produced for that entrypoint, or  
  - A function was produced but it didn’t handle the request (or didn’t exist at the path Vercel was routing to).
- Result: for every request (including `/`), Vercel had no runnable handler or the route didn’t match the function, so it returned **404 NOT_FOUND**.

**Misconception**

- Assuming that “pointing Vercel at a file that exposes a WSGI app” is enough.  
- On Vercel, you must use either:
  - A builder that **knows about WSGI** (e.g. `@ardnt/vercel-python-wsgi`), or  
  - A small adapter that **turns the Vercel request into a WSGI call** and then calls your Django app.

---

## 3. Underlying concept

**Why NOT_FOUND exists**

- Vercel returns NOT_FOUND when **no resource or function is configured to handle that path**.  
- It protects you from silently serving the wrong thing or failing in an unclear way: the platform is saying “I have nothing registered for this URL.”

**Mental model**

- **Vercel = static + serverless:**  
  - Some paths → static files (or front-end app).  
  - Other paths → serverless functions.  
- Each serverless function is a **single entrypoint** (one file, one handler).  
- If you want “every path (e.g. `/(.*)`) to go to Django,” you need:
  - **One** serverless function that is responsible for that.
  - That function must **invoke your Django app** (via a WSGI adapter or a builder that does it).

So:

- **Request path** → Vercel routing (`routes` in `vercel.json`) → **one function** (e.g. `/index.py`).
- That function’s **job** is to turn the HTTP request into a WSGI call to Django and return the response.  
- The WSGI builder does that job; the plain Python runtime does not.

**How this fits framework design**

- Django is built for **long-running processes** (WSGI/ASGI servers).  
- Vercel is **request‑scoped**: one invocation per request.  
- The “adapter” (or builder) is the layer that maps **one Vercel request → one WSGI call → one response**.  
- Without that layer, Vercel never actually “runs” your Django app, so you get NOT_FOUND.

---

## 4. Warning signs and similar mistakes

**What to look for**

- **404 on every path** (including `/`) → routing or entrypoint problem, not a single missing Django URL.
- **Using `@vercel/python` with a file that only exports a WSGI app** → runtime won’t call your app.
- **`dest` without a leading slash** (e.g. `"dest": "index.py"`) → some setups expect `"/index.py"` for the function path.
- **Root Directory wrong** → Vercel builds from another folder, so it never sees your `index.py` / `vercel.json` and no function is created where you expect.

**Similar mistakes**

- Using `@vercel/python` with Flask/FastAPI without exporting the app in the way the runtime expects (or without an adapter).
- Putting `vercel.json` in a subfolder but not setting Root Directory, so Vercel uses the repo root and your config is ignored.
- Assuming “it works locally” implies “it will work on Vercel” without checking that the **deployment contract** (builder + route + entrypoint) is satisfied.

**Code/config smells**

- `vercel.json` has `builds` + `routes` but you never see a successful build or the function in the deployment.
- No `package.json` (or no `@ardnt/vercel-python-wsgi`) when using a third‑party builder that’s an npm package.
- Root Directory not set when the “real” app lives in a subfolder.

---

## 5. Alternatives and trade-offs

**A. Use `@ardnt/vercel-python-wsgi` (current approach)**  
- **Pros:** Minimal config, one `index.py`, works with existing Django layout.  
- **Cons:** Third‑party builder; dependency on its maintenance.

**B. Run Django in a Docker/container on another platform (Railway, Render, Fly.io, etc.)**  
- **Pros:** No WSGI↔serverless adapter; closer to “normal” Django deployment.  
- **Cons:** Not serverless; you manage (or pay for) a long‑running process.

**C. Use Vercel’s official pattern (e.g. Django in `api/` with their structure)**  
- **Pros:** Aligns with Vercel’s own examples.  
- **Cons:** May require moving or renaming your project to match their layout (e.g. `api/wsgi.py`, `api/settings.py`).

**D. Adapter in code (no third‑party builder)**  
- **Pros:** Full control; no npm builder.  
- **Cons:** You maintain the request↔WSGI conversion and any edge cases (streaming, headers, etc.).

**Recommendation:** For this repo, **A** is the most straightforward: keep `@ardnt/vercel-python-wsgi`, `index.py`, and `"dest": "/index.py"`, and ensure Root Directory and env vars are set. If you later need a different platform or more control, **B** or **D** are good alternatives.
