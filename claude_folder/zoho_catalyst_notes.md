# ZOHO CATALYST - COMPLETE NOTES
> Compiled from official Zoho Catalyst documentation
> For reference during development & learning

---

## 1. WHAT IS CATALYST?

Zoho Catalyst is a **fully-managed, cloud-computing platform** that provides powerful infrastructure
for application building. It offers both:
- **FaaS** (Functions as a Service) — serverless functions
- **PaaS** (Platform as a Service) — full app hosting (AppSail)

**Key point:** You write the code, Zoho handles everything else (servers, scaling, security, hosting).

---

## 2. MAJOR SERVICES (11 Services)

| # | Service | What It Does |
|---|---------|--------------|
| 1 | **Serverless** | Backend functions — your business logic runs here |
| 2 | **Cloud Scale** | Storage, security, DB, caching, authentication — infrastructure layer |
| 3 | **Zia Services** | AI/ML — OCR, AutoML, Text Analytics, Image Moderation |
| 4 | **DevOps** | Monitoring, testing, quality assurance |
| 5 | **SmartBrowz** | Headless browser — web scraping, crawling, PDF generation |
| 6 | **ConvoKraft** | AI chatbot builder — conversational assistants |
| 7 | **Job Scheduling** | Cron jobs — scheduled/recurring tasks |
| 8 | **Slate** | Frontend hosting — deploy React, Next.js, Vue, etc. |
| 9 | **Pipelines** | CI/CD — automated deployments |
| 10 | **QuickML** | No-code ML pipeline builder |
| 11 | **Signals** | Event Bus — event-driven communication between apps |
| 12 | **ZEST** | REST API development tool with auto SDK generation |

---

## 3. SERVERLESS FUNCTIONS (Backend Logic)

### 3.1 Function Types

| Type | Purpose | When to Use |
|------|---------|-------------|
| **Basic I/O** | Simple input/output, basic HTTP operations | Simple data processing, quick tasks |
| **Advanced I/O** | Full HTTP control — Headers, Request/Response objects, multiple APIs | REST APIs, complex backend logic, CRUD operations |
| **Event Function** | Triggered by Event Listeners (not manual invocation) | React to events (file upload, DB change, etc.) |
| **Cron Function** | Time-based — one-time or recurring schedule | Scheduled tasks: backups, syncs, reports |
| **Integration Function** | Connect with other Zoho services | Zoho CRM, Books, etc. integration |
| **Browser Logic** | Browser-based tasks via SmartBrowz | Web scraping, screenshot generation |

### 3.2 Supported Languages
- **Java**
- **Node.js**
- **Python**

### 3.3 Important Rules
- Each function type has its **own default boilerplate code**
- **NEVER copy-paste code between different function types** — they load different modules
- Functions can be protected using **Security Rules** (JSON file with access definitions)

### 3.4 Supporting Components
- **API Gateway** — routing and authentication
- **Security Rules** — access control (auto-enabled for Basic/Advanced I/O)
- **Logs** — execution monitoring
- **APM** — Application Performance Monitoring
- **Circuits** — workflow orchestration (chain multiple functions)

### 3.5 AppSail (PaaS Alternative)
- Full framework support (Express.js, Flask, Spring Boot, etc.)
- Dependency management
- Auto-scaling server instances
- Use when you need more than what serverless functions can offer

### 3.6 Circuits (Workflow Orchestration)
- Chain multiple Basic I/O functions together
- Concurrent or sequential execution
- Configure conditions and data flow
- Drag-and-drop console builder available

---

## 4. DATA STORE (Database)

### 4.1 What Is It?
A cloud-based **relational database** (like MySQL/PostgreSQL but fully managed by Zoho).
You can create tables via the console without writing code, or use ZCQL queries.

### 4.2 Key Features
- Visual console for table creation and management
- **ZCQL** (Zoho Catalyst Query Language) — SQL-like query language
- Bulk Read, Bulk Write, Bulk Delete support
- Advanced search on indexed columns
- Metrics tracking (table count, row count history)

### 4.3 Access Methods
- Java SDK, Node.js SDK, Python SDK, Web SDK
- REST API
- ZCQL queries

### 4.4 Scopes & Permissions

**3 Table Scopes (who can see the data):**

| Scope | Meaning |
|-------|---------|
| **Global** | Entire dataset accessible to all users |
| **Org** | Restricted to organization members only |
| **User** | Restricted to individual user's own data only |

**4 Table Permissions (what actions are allowed):**

| Permission | Action |
|-----------|--------|
| **Select** | View/read data (READ) |
| **Update** | Modify existing data (UPDATE) |
| **Insert** | Add new data (CREATE) |
| **Delete** | Remove data or table (DELETE) |

- Permissions are **role-based** — configure separately for each user role
- Navigate to: Table → "Scopes & Permissions" section in console
- Only **table-level** access control is available (no row-level or column-level permissions)

---

## 5. AUTHENTICATION (User Management)

### 5.1 Two Primary Methods

**A. Native Catalyst Authentication:**
1. **Hosted Authentication** — Zoho-hosted login page (easiest setup)
2. **Embedded Authentication** — Login form embedded within your app

**B. Third-Party Authentication:**
- Google, Zoho sign-in providers
- Social logins integration

> You can use **all three methods simultaneously** in a single app.
> At least **one authentication method must be configured** before adding users.

### 5.2 User Management Capabilities
- Add/remove end-users
- Enable/disable accounts
- Reset passwords
- Generate user sign-in code snippets for app integration

### 5.3 Configuration Features
- Google & Zoho sign-in providers
- Custom login/signup form design
- User roles (define access levels)
- CORS & iFrame domain authorization
- Custom email templates (invitations, password reset)
- Whitelisting (custom validation, authorized domains)

### 5.4 Access Methods
- Catalyst Console (web UI)
- SDKs: Java, Node.js, Python, Web
- REST APIs

### 5.5 Cross-Domain Authentication
- Required when frontend and backend are on **different domains**
- Must configure **CORS** — whitelist both backend & frontend domains
- Use **Authorized Domains** feature in the Authentication section
- Ensure both domains are whitelisted for proper cookie/token flow

---

## 6. STRATUS (Object/File Storage)

### 6.1 What Is It?
A cloud storage solution for storing any type of data as **objects** within **buckets**.
(Similar to AWS S3 / Google Cloud Storage)

### 6.2 Core Concepts

**Buckets:**
- Storage containers that can hold unlimited objects
- Each bucket gets a unique **Bucket URL** on creation
- Accessible via console or programmatically

**Objects:**
- Any data format = object (files, images, documents, etc.)
- Each upload generates a unique **Object URL**
- Supports path-based organization (directory structure)

### 6.3 Key Features
- **Multipart Upload** — for large files (2GB+, parallel upload)
- **Range-based Download** — download specific parts of a file
- **Malware Scanning** — auto scan, delete infected files, send notifications
- **Encryption** — data at rest & in flight
- **Custom Permissions** — JSON-based per-object permissions
- **HIPAA Compliance** — PII/ePHI mode with audit logging
- **Versioning** — unique version ID for each object iteration
- **CORS** — cross-domain resource sharing configuration
- **Event Listeners** — trigger actions on bucket activities
- **Migration** — import from Amazon S3, Google Cloud Platform

### 6.4 SDKs Available
- Server: Java, Node.js, Python
- Client: Web, Android, iOS, Flutter
- REST APIs also available

---

## 7. SLATE (Frontend Hosting)

### 7.1 What Is It?
A frontend deployment & hosting service — host your React/Next.js/Vue app here.

### 7.2 Supported Frameworks
Next.js, Angular, Astro, React, SolidJS, Preact, Svelte, Vue, Vite, Nuxt
(+ other frameworks are also supported)

### 7.3 Key Features
- Free SSL certificates
- Secured environment variables
- Multiple apps per project
- Multiple deployments per app
- Preview URLs (test without affecting production)
- Custom domain mapping
- Rollback to previous versions
- Auto-detect framework & handle build/deploy process

### 7.4 Three Deployment Methods

**1. Git Integration (Best for teams):**
- Connect GitHub, GitLab, or Bitbucket
- Auto Deploy — automatic deployment on code push
- Starter templates available

**2. Console Upload (Quick method):**
- Drag & drop a zip file in the console
- Deployed within minutes

**3. Catalyst CLI (Developer-friendly):**
```bash
catalyst deploy
```

### 7.5 Build & Deploy Flow
1. Submit source code (Git / Upload / CLI)
2. Automatic build processing
3. Cloud hosting
4. Unique access URL generated
5. Auto-deploy on push for Git-linked repos

Internally uses **Catalyst Pipelines** for CI/CD.

---

## 8. MULTITENANCY DEMO (Reference Project)

### 8.1 Project Structure
```
catalyst-multitenancy-demo/
├── functions/
│   └── multi_tenant_demo_function/    # Backend serverless functions
├── taskManagerClient/                  # Frontend client
├── catalyst.json                       # Project config
└── README.md
```

### 8.2 Tech Stack
- Backend: Catalyst Serverless Functions
- Frontend: JavaScript (49.4%), HTML (21%), CSS (29.6%)
- Services: Slate + CloudScale Authentication (embedded + public signups)

### 8.3 Setup Steps
1. Clone repository
2. Create new Catalyst project via console
3. Enable Slate & CloudScale Authentication
4. Update `catalyst.json` with system path
5. Run `catalyst init`
6. Run `catalyst serve` (local development)
7. Run `catalyst deploy` (production)

### 8.4 Key Configuration
- `API_BASE` in `main.js` must point to the correct Catalyst project URL
- `catalyst.json` needs local system path configured

---

## 9. AVAILABLE SDKs

| Language | Version |
|----------|---------|
| Java | v1 |
| Node.js | v2 |
| Python | v1 |
| Web | v4 |
| Android | v2 |
| iOS | v2 |
| Flutter | v2 |

---

## 10. CLI COMMANDS (Quick Reference)

| Command | Purpose |
|---------|---------|
| `catalyst login` | Authenticate with Zoho account |
| `catalyst init` | Initialize project locally |
| `catalyst serve` | Start local development server |
| `catalyst deploy` | Deploy to Catalyst cloud |
| `catalyst functions:create` | Create a new function |
| `catalyst client:create` | Create a frontend client |
| `catalyst --version` | Check CLI version |

---

## 11. TYPICAL PROJECT STRUCTURE

```
my-catalyst-project/
├── catalyst.json              # Project configuration
├── functions/
│   └── my-function/           # Backend function
│       ├── index.js           # Function code (Node.js)
│       └── catalyst-config.json
├── client/                    # Frontend (Slate/Web Client)
│   ├── index.html
│   ├── css/
│   └── js/
└── .catalyst/                 # Internal catalyst config
```

---

## 12. IMPORTANT LINKS

| Resource | URL |
|----------|-----|
| Documentation | https://docs.catalyst.zoho.com/en/ |
| Console | https://console.catalyst.zoho.com |
| Tutorials | https://docs.catalyst.zoho.com/en/tutorials/ |
| Serverless Intro | https://docs.catalyst.zoho.com/en/serverless/getting-started/introduction/ |
| Functions | https://docs.catalyst.zoho.com/en/serverless/help/functions/introduction/ |
| Data Store | https://docs.catalyst.zoho.com/en/cloud-scale/help/data-store/introduction/ |
| Data Store Permissions | https://docs.catalyst.zoho.com/en/cloud-scale/help/data-store/scopes-and-permissions/ |
| Authentication | https://docs.catalyst.zoho.com/en/cloud-scale/help/authentication/introduction/ |
| Cross-Domain Auth | https://docs.catalyst.zoho.com/en/cloud-scale/help/authentication/cross-domain-access/ |
| Stratus | https://docs.catalyst.zoho.com/en/cloud-scale/help/stratus/introduction/ |
| Slate | https://docs.catalyst.zoho.com/en/slate/help/introduction/ |
| Multitenancy Demo | https://github.com/vigneshiamvk/catalyst-multitenancy-demo |

---

## 13. KEY CONCEPTS SUMMARY (Quick Revision)

1. **Catalyst = Serverless Platform** — write code, no infrastructure management needed
2. **Functions = Backend** — 5 types (Basic I/O, Advanced I/O, Event, Cron, Integration)
3. **Data Store = Database** — relational DB with ZCQL, role-based table-level access
4. **Stratus = File Storage** — S3-like object storage with buckets
5. **Slate = Frontend Hosting** — deploy React/Vue/Next.js with Git integration
6. **Authentication = User Management** — login/signup, roles, social login
7. **CLI = Developer Tool** — init, serve, deploy everything from terminal
8. **Circuits = Workflow** — chain multiple functions together
9. **Signals = Event Bus** — event-driven communication
10. **Pipelines = CI/CD** — automated deployments
