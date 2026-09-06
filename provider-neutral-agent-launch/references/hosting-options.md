A **full-time environment** (a persistent server or always-on app runtime) requires platforms that host continuous background processes, full-stack web frameworks, or databases without spinning down after inactivity.

Platforms are categorized below by operational structure, highlighting both their free capabilities and paid upgrades.

---

### **1. Cloud PaaS (Platform as a Service)**

*Best for full-stack apps (Node.js, Python, Go, Docker) that need background jobs, live websockets, or connected databases.*

* **Render**
* **Free Tier:** Includes 750 free instance hours per month for web services, 100 GB bandwidth, and automatic Git deployments.
* **Catch:** Free web services spin down after 15 minutes of inactivity (takes ~30-60 seconds to wake up on the next request). Free Postgres databases expire after 30 days unless upgraded.
* **Paid:** Starts at **$7/month** per service for 24/7 always-on instances without cold starts.


* **Fly.io**
* **Free Tier:** Very strict/limited trial allowance rather than a true full free tier, but allows running low-resource edge micro-containers for testing.
* **Paid:** Micro instances start at **~$2 to $5/month** based on usage (pay-as-you-go per second for CPU/RAM). Ideal for always-on low-latency apps worldwide.


* **Koyeb**
* **Free Tier:** Offers 1 free micro instance (512 MB RAM, 0.25 vCPU) that runs continuous web services with automatic SSL and Git integration.
* **Paid:** Starts at **~$5.50/month** for dedicated resources and auto-scaling.


* **Railway**
* **Free Tier:** Provides a **$5 execution credit trial** (one-time) for new users to build and test.
* **Paid:** Transitions to a usage-based Hobby plan (**$5/month base** + usage), making it one of the easiest developer experiences for persistent full-stack setups.



---

### **2. Infrastructure & Virtual Private Servers (VPS)**

*Best for full control over an entire Linux OS to run system daemons, multiple databases, or custom cron jobs.*

* **Oracle Cloud (Always Free)**
* **Free Tier:** The most generous permanent free tier in the industry. Gives up to **4 Arm-based Ampere A1 cores and 24 GB of RAM** (divisible into 1–4 VMs), plus 200 GB of block storage.
* **Catch:** Requires valid credit card verification; idle instances may be flagged or reclaimed if compute usage drops near 0% for extended periods.
* **Paid:** Pay-as-you-go pricing if you scale beyond the free allocations.


* **Hetzner / DigitalOcean / Linode / Vultr**
* **Free Tier:** None (only short-term promotional sign-up credits, usually $100-$200 for 60 days).
* **Paid:** DigitalOcean, Vultr, and Linode start at **$4–$6/month**. Hetzner offers entry-level cloud VMs starting around **€4–€5/month** with high CPU/RAM value in Europe and North America.



---

### **3. Serverless & Frontend Platforms**

*Best for APIs, edge functions, and frontends. (Note: These use event-driven serverless architectures rather than a traditional persistent server instance).*

* **Vercel**
* **Free Tier:** Generous for Next.js and frontend frameworks. Includes 100 GB bandwidth, deployment previews, and serverless API functions.
* **Catch:** Functions have execution timeouts (5-minute maximum execution) and cold starts; not meant for background workers or persistent WebSockets.
* **Paid:** Pro plan starts at **$20/user/month**.


* **Cloudflare (Pages + Workers)**
* **Free Tier:** Unlimited bandwidth for static sites (Pages) + 100,000 requests/day on Workers (edge serverless functions).
* **Paid:** Workers Paid starts at **$5/month** for 10 million requests/month and higher CPU limits.



---

### **Summary Comparison**

| Platform | Best For | Always-On Free Tier? | Paid Starting Price |
| --- | --- | --- | --- |
| **Oracle Cloud** | Self-managed Linux VM | **Yes** (24 GB RAM ARM tier) | Usage-based |
| **Koyeb** | Git-to-deploy PaaS | **Yes** (1 micro service) | ~$5.50/mo |
| **Render** | Docker / Node / Python | **Partial** (spins down on idle) | $7/mo |
| **Fly.io** | Global edge containers | **Trial only** | ~$2–$5/mo |
| **Hetzner / DigitalOcean** | Dedicated VPS root access | **No** (promos only) | ~$4–$6/mo |
| **Vercel / Cloudflare** | Frontend + Serverless APIs | **Yes** (request-based, not continuous) | $5–$20/mo |
| **
| **

* **GitHub Pages**
* **Free Tier:** Completely free static hosting with custom domain support, unlimited bandwidth (up to 100 GB/month soft limit), and direct integration with Git repositories and GitHub Actions.
* **Catch:** Static-only; cannot run backend code, databases, or long-lived server processes (HTML/CSS/JS/WASM only).
* **Paid:** Free for public and private repositories (advanced enterprise features available on paid GitHub team plans).


* **GitHub Actions** (as an automation/cron runtime)
* **Free Tier:** 2,000 free minutes per month for public repositories (and 500 minutes for private repos on free accounts).
* **Catch:** Not meant for continuous 24/7 hosting. Jobs time out after 6 hours and are triggered by events (cron schedules, git pushes, manual webhooks), making it ideal for scheduled tasks, scrapers, and CI/CD pipelines.
* **Paid:** Pay-as-you-go per minute after free allotment (~$0.008/min for Linux runners).

Below are additional popular hosting and application deployment platforms, categorized by how they run workloads.

---

### **1. Container-Native PaaS (Persistent Backends & Webhooks)**

*Best for hosting custom backends (Node.js, Go, Python, Rust, Java), background workers, or databases using continuous containers.*

* **Google Cloud Run**
* **Free Tier:** 2 million requests per month, 180,000 vCPU-seconds, and 360,000 GiB-seconds of memory.
* **Catch:** Scales to zero when idle (cold start on new requests). Requires credit card verification upon signup.
* **Paid:** Pay-as-you-go based on exact vCPU and memory consumption down to the millisecond.


* **Zeabur**
* **Free Tier:** Offers $5 in free execution credits every month, which can host micro-services, APIs, or lightweight databases without sleeping.
* **Paid:** Usage-based billing once monthly free credits are depleted.


* **Glitch**
* **Free Tier:** Instant Node.js sandbox environment with continuous auto-saves.
* **Catch:** Apps auto-sleep after 5 minutes of inactivity and are capped at 1,000 execution hours per month.
* **Paid:** **$8–$10/month** for always-on instances, higher CPU/RAM limits, and unlimited execution hours.


* **Northflank**
* **Free Tier:** Micro sandbox plan allowing 1 micro service + 1 database.
* **Paid:** Starts at **$6/month** plus resource usage for auto-scaling production workloads.



---

### **2. Frontend & Static Hosting Platforms**

*Best for single-page applications (React, Vue, Svelte) or JAMstack frontends.*

* **Netlify**
* **Free Tier:** 100 GB bandwidth per month, 300 build minutes, automatic SSL, and 125,000 serverless function invocations.
* **Paid:** Pro tier starts at **$19/user/month** for advanced security, split testing, and higher team limits.


* **Firebase Hosting (Google)**
* **Free Tier:** 10 GB storage and 360 MB/day data transfer. Integrates directly with Firebase Auth, Firestore, and Cloud Functions.
* **Paid:** Blaze Plan (Pay-as-you-go) charges pennies per GB beyond the free quota.


* **Surge.sh**
* **Free Tier:** Deploy static sites directly via CLI in seconds with custom domain support.
* **Paid:** Professional tier is **$13/month** for custom SSL, basic auth, and redirect routing.



---

### **3. Specialized Language & Developer Platforms**

* **PythonAnywhere**
* **Free Tier:** 1 free Python web app (Django, Flask, FastHTML) on a `yourusername.pythonanywhere.com` subdomain.
* **Catch:** Limited compute power (100 CPU seconds per day) and restricted outbound internet access (whitelisted APIs only on free tier).
* **Paid:** Beginner paid plan starts at **$5/month** for custom domain support and full outbound net access.


* **Appwrite Sites**
* **Free Tier:** 5 GB bandwidth, 2 GB storage, and 750k serverless function runs.
* **Paid:** Pro plan scales for team usage and production SLAs.



---

### **4. Self-Hosted PaaS (The Low-Cost Hybrid)**

*If you buy a cheap VPS (e.g., $4–$5/month on Hetzner or DigitalOcean), you can install these open-source tools to turn it into your own private Vercel or Heroku.*

* **Coolify / CapRover / Dokku**
* **Cost:** 100% Free & Open Source Software. You only pay the cost of the underlying server ($0 on Oracle Always-Free, or ~$4/month on cheap cloud providers).
* **Features:** Provides Git-push deploys, continuous integration, automatic SSL via Let's Encrypt, and 1-click database provisioning (PostgreSQL, Redis, MySQL) without platform lock-in.



---

### **Overview**

| Platform | Type | Always-On Free Tier? | Paid Starting Price |
| --- | --- | --- | --- |
| **Google Cloud Run** | Serverless Containers | **Yes** (Generous monthly invocation pool) | Usage-based |
| **Netlify** | Frontend / Serverless | **Yes** (100 GB/month) | $19/mo |
| **Firebase Hosting** | Frontend / Mobile Backends | **Yes** (10 GB storage) | Pay-as-you-go |
| **PythonAnywhere** | Python Web Apps | **Yes** (Restricted outbound access) | $5/mo |
| **Coolify (Self-Hosted)** | Private PaaS Software | **Yes** (Software is free; pay for server) | ~$4–$5/mo VPS |

Expanding beyond traditional PaaS, static, and cloud VPS options, here are additional categories and platforms used for hosting, backend infrastructure, and persistent environments:

---

### **1. Managed Database Hosting (Free & Paid)**

*Because running persistent databases on free web hosts (like Render or Railway) often comes with strict limits or data expiration, developers usually pair backend app hosts with dedicated managed database services.*

* **Supabase**
* **Free Tier:** 2 active PostgreSQL projects with **500 MB database storage** each, 5 GB file storage, and integrated Auth.
* **Catch:** Free databases automatically pause after 1 week of zero activity.
* **Paid:** Starts at **$25/month** for always-on instances, higher storage limits, and daily backups.


* **Neon**
* **Free Tier:** Serverless Postgres with **0.5 GB of storage** per project and instant branching capabilities.
* **Catch:** Compute scales down to zero after 5 minutes of inactivity (causes a minor cold start on the next query).
* **Paid:** Starts at **$19/month** for always-on compute and scaling.


* **Turso**
* **Free Tier:** SQLite-based database at the edge offering up to **9 GB total storage** and 1 billion row reads per month.
* **Paid:** Starts at **$29/month**.


* **MongoDB Atlas**
* **Free Tier:** 1 free M0 cluster (512 MB storage) shared across users, ideal for lightweight document/NoSQL storage.
* **Paid:** Dedicated clusters start at **~$57/month** (or pay-as-you-go serverless instance tiers).



---

### **2. Alternative Backend & Docker Hosts**

* **SnapDeploy**
* **Free Tier:** Deploy up to **4 containers** (512 MB RAM each) without a credit card.
* **Catch:** Containers sleep after inactivity and take 10–30 seconds to wake. Custom domains require a paid plan.
* **Paid:** Always-On instances start at **$12/month** per container.


* **Deno Deploy**
* **Free Tier:** **1 million requests per month**, 15 CPU hours, and 20 GB egress for running Deno/TypeScript scripts natively across 35+ global edge regions.
* **Paid:** Starts at **$10/month** for increased CPU allowances and request limits.


* **Hatchable**
* **Free Tier:** Includes hosting + a free PostgreSQL database + 1 GB storage with custom subdomain support.
* **Catch:** Free apps require a platform badge.
* **Paid:** **$12/month** Builder plan for unlimited apps and custom domain mapping.



---

### **3. Niche & Developer Environment Hosting**

* **Replit**
* **Free Tier:** Full cloud-based IDE with temporary dev environments.
* **Catch:** Apps sleep after short idle periods; no longer offers permanent free background hosting for production deployments.
* **Paid:** Core plans start around **$12–$20/month** for always-on Reserved VM deployments and custom domains.


* **Wasmer Edge**
* **Free Tier:** Hosting built specifically for WebAssembly (WASM) packages, offering fast execution with lightweight edge memory footprints.
* **Paid:** Pro options scale for commercial bandwidth and dedicated SLAs.



---

### **Summary of Supplementary Categories**

| Service | Category | Free Tier Catch | Paid Starting Price |
| --- | --- | --- | --- |
| **Supabase / Neon** | Managed PostgreSQL | Pauses or sleeps after inactivity | $19–$25/mo |
| **Turso / MongoDB Atlas** | SQLite / NoSQL DB | Storage caps (512 MB–9 GB) | Pay-as-you-go / $29/mo |
| **Deno Deploy** | Edge TypeScript APIs | Isolate runtime limits | $10/mo |
| **SnapDeploy** | Docker Containers | Spins down when idle | $12/mo |
| **Replit** | Interactive Cloud IDE | Development-only; sleeps on idle | ~$12–$20/mo |

Beyond PostgreSQL, SQLite, and basic NoSQL, database platforms cover **time-series, in-memory caching, multi-model document stores, vector databases, and hyperscaler managed clouds**.

---

### **1. In-Memory, Key-Value & Caching Databases**

*Best for session stores, job queues, real-time leaderboards, and fast caching.*

* **Upstash (Serverless Redis & Vector)**
* **Free Tier:** **10,000 requests/day** (or 500k commands/month) and **256 MB storage** for Redis; **10,000 vector writes/reads** for Upstash Vector.
* **Catch:** Strict command rate-limiting once free limits are reached.
* **Paid:** Pay-as-you-go starting at **$0.20 per 100k commands** or **$10/month** fixed limits.


* **Redis Cloud**
* **Free Tier:** 1 free database instance with **30 MB of memory** and persistent storage.
* **Paid:** Flexible plans starting at **$5/month**.



---

### **2. Managed Relational Databases (MySQL & Distributed SQL)**

* **Aiven**
* **Free Tier:** Fully managed **always-free MySQL** (1 vCPU, 1 GB RAM, 1 GB storage) running on dedicated single-node VMs.
* **Catch:** Services pause after prolonged inactivity (notified via email).
* **Paid:** Starts at **$19/month** for production high-availability nodes.


* **CockroachDB Serverless (Distributed SQL)**
* **Free Tier:** **10 GB storage** and 50M Request Units (RU) per month. Provides global scale and PostgreSQL wire compatibility.
* **Paid:** Pay-as-you-go at **$1 per 10M RUs** and **$0.50/GB-month**.


* **Oracle Autonomous Database**
* **Free Tier:** Includes **2 Always Free Autonomous Databases** (Transaction Processing or Data Warehouse) with 1 vCPU and **20 GB storage** each.
* **Paid:** Auto-scales billed on CPU second usage.



---

### **3. Native Edge & Vector Databases (AI / Embeddings)**

* **Cloudflare D1 (Edge SQL)**
* **Free Tier:** **5 GB total storage**, 5 million row reads per day, and 100,000 row writes per day built on SQLite.
* **Catch:** Native access requires running inside Cloudflare Workers/Pages.
* **Paid:** Workers Paid plan at **$5/month** includes 25 GB storage and 25M row reads/day.


* **Pinecone (Vector DB for AI)**
* **Free Tier:** 1 free project with **2 GB storage** (up to ~100k 768-dimensional vectors with metadata).
* **Paid:** Standard plan starts at **$50/month** (or serverless pay-as-you-go per query).


* **Qdrant Cloud**
* **Free Tier:** 1 permanent cluster with **1 GB RAM / 4 GB disk storage** for vector search workloads.
* **Paid:** Starts at **$25/month** for dedicated cluster nodes.



---

### **4. Big Three Cloud Managed Tiers (AWS, GCP, Azure)**

*Best for production compliance, enterprise integration, and heavy ecosystem usage.*

* **AWS Free Tier (RDS & DynamoDB)**
* **DynamoDB (Always Free):** **25 GB storage** and 25 WCU / 25 RCU (enough for ~200M requests/month).
* **Amazon RDS (12-Month Trial):** **750 hours/month** of single-AZ `db.t2.micro` or `db.t3.micro` instance (PostgreSQL, MySQL, or MariaDB) for 1 year.
* **Paid:** Standard pay-as-you-go hourly instance pricing.


* **Google Cloud Firestore & Bigtable**
* **Firestore (Always Free):** **1 GB total storage**, 50,000 reads, 20,000 writes, and 20,000 deletes per day.
* **Paid:** Pay-as-you-go past daily free limits.


* **Azure Cosmos DB**
* **Free Tier:** **1,000 RU/s throughput** and **25 GB storage** free forever per account (supports NoSQL, MongoDB API, and PostgreSQL).
* **Paid:** Consumption-based billing past 1k RU/s.



---

### **Summary Matrix**

| Provider | DB Engine | Always-On Free Tier? | Paid Starting Price |
| --- | --- | --- | --- |
| **Upstash** | Redis / Vector | **Yes** (10k requests/day) | $0.20 per 100k cmds |
| **Aiven** | Managed MySQL | **Yes** (1 GB RAM / 1 GB Storage) | $19/mo |
| **CockroachDB** | Distributed SQL | **Yes** (10 GB storage) | Pay-as-you-go |
| **Cloudflare D1** | Edge SQLite | **Yes** (5 GB / 5M daily reads) | $5/mo (Workers plan) |
| **Pinecone / Qdrant** | Vector DB (AI) | **Yes** (1–2 GB storage) | $25–$50/mo |
| **AWS DynamoDB** | NoSQL | **Yes** (25 GB storage) | Pay-as-you-go |
| **Azure Cosmos DB** | Multi-model / NoSQL | **Yes** (25 GB storage / 1k RU) | Pay-as-you-go |

### **Backend Platforms (Serverless, Containers & PaaS)**

#### **1. FastComet / WebHostingPad / InfinityFree (Classic Shared PHP/Node Backends)**

* **Free Tier:** **InfinityFree** offers free PHP/MySQL hosting with cPanel-like access, standard webmail, unlimited bandwidth, and zero ads.
* **Catch:** Restricted execution times per script; no persistent daemon processes or custom background workers.
* **Paid:** Upgrades start around **$2.50 to $5/month** for full SSH access and custom binaries.

#### **2. AWS Elastic Beanstalk & App Runner**

* **Free Tier:** **AWS Elastic Beanstalk** falls under the AWS 12-month free tier (`t2.micro`/`t3.micro` EC2 instances for 750 hours/month). **AWS App Runner** offers a pay-as-you-go container runner with scale-to-zero compute.
* **Catch:** App Runner charges for memory provisioned even when scaled to zero (~$0.007/GB-hour).
* **Paid:** Elastic Beanstalk is free to use (you pay for underlying EC2/ALB resources, ~$5–$15/month). App Runner starts around **$5/month**.

#### **3. Serverless Framework / AWS Lambda & Azure Functions**

* **Free Tier:** **AWS Lambda** provides **1 million free requests** and 400,000 GB-seconds of compute every month. **Azure Functions** provides **1 million free executions** and 400,000 GB-s of consumption.
* **Catch:** Stateless execution model; cold starts on infrequent requests.
* **Paid:** Pay-as-you-go per invocation ($0.20 per million requests beyond free tier).

#### **4. Cyclic (Serverless Node.js / Python)**

* **Free Tier:** Deploy apps directly from GitHub with automatic serverless wrapper integration, free custom domain SSL, and instant builds.
* **Catch:** Free tiers scale down to zero on inactivity and cap memory usage.
* **Paid:** Tiered plans start at **$6/month** for always-on worker processes.

---

### **2. Frontend & Static Site Hosting**

#### **1. GitLab Pages**

* **Free Tier:** Completely free static hosting directly from GitLab CI/CD pipelines, custom domain support, automatic Let's Encrypt SSL certificates, and 10 GB total repository storage.
* **Catch:** Static-only assets (HTML/CSS/JS).
* **Paid:** Included free across self-hosted and paid GitLab SaaS tiers.

#### **2. AWS Amplify**

* **Free Tier:** **1,000 build minutes/month**, **5 GB storage**, and **15 GB served bandwidth/month** for 12 months.
* **Catch:** Free tier expires after 1 year.
* **Paid:** Pay-as-you-go ($0.01/GB served, $0.01/build minute).

#### **3. Azure Static Web Apps**

* **Free Tier:** **100 GB bandwidth/month**, free custom SSL certificates, staging environments for pull requests, and integrated serverless API routes using Azure Functions.
* **Catch:** 250 MB max app size.
* **Paid:** Standard tier is **$9/app/month** for higher enterprise bandwidth.

#### **4. Hostinger / GitHub Gist / CodePen (Sandbox Hosting)**

* **Free Tier:** **CodePen & JSFiddle** offer web-based frontend hosting for HTML/CSS/JS components; **Hostinger** provides trial static site builders.
* **Paid:** Pro tiers start at **$3–$8/month**.

---

### **3. Databases (Relational, Document, Graph & Time-Series)**

#### **1. PlanetScale (Serverless MySQL)**

* **Free Tier:** Limited trial/developer tier with branch-based Git-like database workflows.
* **Catch:** Scaled back its permanent free tier; primary focus is paid developer databases.
* **Paid:** Starts at **$39/month** for auto-scaling serverless database clusters.

#### **2. InfluxDB Cloud (Time-Series Database)**

* **Free Tier:** **1 MB/sec write rate**, **10 MB/sec read rate**, 30-day data retention, and 2 free query tasks. Ideal for IoT metrics and app analytics.
* **Paid:** Serverless usage-based plan starts at **$0.002/GB** ingested.

#### **3. Neo4j AuraDB (Graph Database)**

* **Free Tier:** 1 free graph database instance with up to **200,000 nodes** and **400,000 relationships**.
* **Paid:** Professional tier starts at **$65/month** (or hourly usage).

#### **4. Faunedb / Fauna (Distributed Document-Relational DB)**

* **Free Tier:** **100,000 read operations**, **50,000 write operations**, and **5 GB storage** per month.
* **Catch:** Proprietary FQL / GraphQL query engine.
* **Paid:** Pay-as-you-go starting at **$25/month**.

---

### **Complete Master Matrix**

| Platform | Domain | Primary Free Limits | Paid Upgrade Price |
| --- | --- | --- | --- |
| **AWS Lambda / Azure Functions** | Backend (Serverless) | **1M requests/mo free** | Pay-as-you-go |
| **SnapDeploy** | Backend (Containers) | **4 containers (auto-sleep)** | $12/mo |
| **GitLab Pages** | Frontend (Static) | **10 GB storage / Free SSL** | Included free |
| **Azure Static Web Apps** | Frontend / SSR | **100 GB bandwidth/mo** | $9/app/mo |
| **InfluxDB Cloud** | Database (Time-Series) | **30-day retention / 1 MB/s write** | Pay-as-you-go |
| **Neo4j AuraDB** | Database (Graph) | **200k Nodes / 400k Edges** | $65/mo |
| **Fauna** | Database (Document SQL) | **100k Reads / 5 GB Storage** | $25/mo |

### **1. AI & GPU Compute Platforms (Backend / Inference / Training)**

*Specialized platforms designed to run LLM inference, Python scripts, background AI workers, and fine-tuning workloads on GPUs with serverless scale-to-zero capabilities.*

* **Modal**
* **Free Tier:** **$30/month in free compute credits** every month (covers significant CPU and GPU serverless runtime).
* **Catch:** Python-native framework; requires using their SDK decorator patterns rather than standard Docker containers.
* **Paid:** Usage-based per second for CPU/RAM and GPUs (e.g., Nvidia T4, A10G, H100).


* **RunPod (Serverless & Pods)**
* **Free Tier:** No permanent free compute (occasional sign-up credits).
* **Paid:** Ultra-low-cost GPU hosting starting at **~$0.20/hour** for community instances or pay-per-second serverless endpoints.


* **Replicate**
* **Free Tier:** Free trial runs (~50 free predictions) for testing open-source AI models via API.
* **Paid:** Pay-per-second based on the exact GPU hardware required (e.g., ~$0.000225/sec on Nvidia T4).


* **Beam.cloud**
* **Free Tier:** **10 hours of free GPU runtime** upon sign-up.
* **Paid:** Pay-as-you-go per second for serverless Python workers and containerized GPU jobs.



---

### **2. Edge Backend & API Frameworks**

*Best for ultra-low latency global microservices, API gateways, and edge middleware.*

* **Fastly Compute@Edge**
* **Free Tier:** **$50/month in free credit** for new accounts to run WebAssembly (WASM) microservices directly on Fastly's global edge network.
* **Paid:** Pay-as-you-go based on CPU time and total request volume.


* **Swarms / Val Town**
* **Free Tier:** **Val Town** gives **10,000 free serverless executions/month** to write and host lightweight backend "vals" (JS/TS scripts running on the cloud).
* **Paid:** Pro starts at **$10/month** for higher rate limits and private scripts.



---

### **3. Specialized & Niche Databases**

* **SurrealDB Cloud**
* **Free Tier:** Free multi-tenant development tier combining document, graph, and relational query features in a single engine.
* **Paid:** Usage-based auto-scaling for production clusters.


* **Chroma Cloud / Supavec**
* **Free Tier:** **Supavec** (open-source RAG platform on top of Supabase) and **Chroma Cloud** provide free tiers for storing document embeddings and vector search.
* **Paid:** Tiered pricing based on total vector storage volume and embeddings generated.


* **Memgraph Cloud (Graph DB)**
* **Free Tier:** 1 free trial/community cloud instance for real-time graph storage (an alternative to Neo4j).
* **Paid:** Starts at **~$0.05/hour** for managed cloud instances.



---

### **4. Ephemeral & Environment-as-a-Service (EaaS)**

*Platforms built specifically for on-demand staging, PR preview environments, and integration testing.*

* **Bunnyshell**
* **Free Tier:** Free starter tier to create preview environments directly connected to GitHub/GitLab pull requests.
* **Paid:** Pay-as-you-go per environment-minute (~$0.007/min).


* **Uffizzi**
* **Free Tier:** Open-source platform with a free cloud tier for ephemeral Kubernetes preview environments on pull requests.
* **Paid:** Usage-based resource charges for persistent cluster environments.



---

### **Master Ecosystem Breakdown**

| Service | Primary Domain | Free Allowance | Paid Starting Price |
| --- | --- | --- | --- |
| **Modal** | AI / GPU / Python Workers | **$30/mo credit** | Per-second usage |
| **Beam.cloud** | Serverless GPU Backends | **10 hours GPU trial** | Pay-as-you-go |
| **Val Town** | Lightweight JS/TS Backends | **10,000 runs/mo** | $10/mo |
| **Fastly Compute** | Edge WASM Runtime | **$50/mo credit** | Usage-based |
| **SurrealDB Cloud** | Multi-Model / Graph DB | **Free Dev Tier** | Usage-based |
| **Bunnyshell** | PR Preview Environments | **Starter Free Tier** | ~$0.007/env-min |

Here is the final extended breakdown covering remaining niche, specialized, self-hosted, edge, enterprise, and decentralized options across backend, frontend, and databases.

---

### **1. Specialized & Alternative Backend Hosts**

* **HelioHost**
* **Free Tier:** Community-run, non-profit host offering **1 GB of storage**, supporting Python, Node.js, PHP, Java, and ASP.NET along with free MariaDB/PostgreSQL databases.
* **Catch:** Daily signup limits; requires staying active on forums to prevent account cleanup.
* **Paid:** One-time donation tiers for additional resources and dedicated hardware.


* **Dada Cloud**
* **Free Tier:** Git-push PaaS tailored for Next.js, FastAPI, static apps, and containerized backends.
* **Paid:** Pay-as-you-go billing based on active memory/vCPU usage.


* **Scaleway (Serverless Functions & Containers)**
* **Free Tier:** **75,000 GB-seconds of container compute** and 100,000 requests per month free.
* **Paid:** Ultra-competitive European cloud pricing starting at fractions of a cent per compute hour.


* **Alibaba Cloud / Tencent Cloud (International Tiers)**
* **Free Tier:** Free trials granting 12-month access to Elastic Compute Service (ECS) VMs and serverless function instances for verified international developers.
* **Paid:** Usage-based pay-as-you-go.



---

### **2. Specialized Frontend & Edge Networks**

* **Fleek (Web3 & IPFS Frontend Hosting)**
* **Free Tier:** Deploy static sites directly to IPFS and decentralized storage networks (Arweave, Filecoin) with custom domain and SSL support.
* **Paid:** Pro plan starting at **$20/month** for advanced CDN edge caching and team features.


* **Stormkit**
* **Free Tier:** Specialized hosting for Javascript frontends (Vue, Nuxt, React, Angular) offering 50 GB bandwidth/month and automatic staging deployments.
* **Paid:** Starts at **$15/month** for team collaboration and self-managed cloud connectors.


* **Kinsta (Static Site Hosting)**
* **Free Tier:** Up to **100 static deployments**, 100 GB bandwidth, and 600 build minutes per month powered by Cloudflare's edge network.
* **Paid:** Focused on paid managed WordPress and application hosting (starts at **$35/month**).



---

### **3. Niche, Time-Series & Enterprise Databases**

* **YugabyteDB Managed (Distributed SQL)**
* **Free Tier:** 1 free single-node cluster with **2 vCPU, 4 GB RAM, and 10 GB disk storage** (PostgreSQL-compatible distributed database).
* **Paid:** Starts at **~$0.25/hour** for multi-region fault-tolerant clusters.


* **QuestDB Cloud (Time-Series)**
* **Free Tier:** High-performance SQL time-series database trial with free execution credits for financial metrics, market data, and IoT telemetry.
* **Paid:** Instance-based billing starting at **$0.08/hour**.


* **SingleStoreDB Cloud**
* **Free Tier:** **$600 in free compute credits** to run real-time analytical and vector search workloads across unified SQL engines.
* **Paid:** On-demand credit purchasing.


* **Hydra (Columnar Postgres for Analytics)**
* **Free Tier:** Free developer tier offering open-source columnar PostgreSQL designed for fast aggregate queries and data warehousing.
* **Paid:** Fully managed production cloud instances.



---

### **4. Decentralized & Peer-to-Peer Backend/Data Platforms**

* **Internet Computer (ICP / Canisters)**
* **Free Tier:** Developer grants and initial cycles to deploy "canisters" (smart-contract-like persistent WebAssembly backend/frontend units that run forever on-chain).
* **Paid:** Purchase ICP tokens to convert into execution "cycles" (extremely low ongoing cost).


* **GunDB / Ceramic Network**
* **Free Tier:** 100% open-source, decentralized peer-to-peer graph databases that store data client-side and sync across mesh networks without requiring centralized servers.
* **Cost:** Free (you run or connect to open peer nodes).



---

### **Grand Overview Matrix**

| Service | Category | Free Allowance | Paid Starting Price |
| --- | --- | --- | --- |
| **HelioHost** | Backend / Full-Stack | **1 GB Storage / Full Stack** | One-time donation |
| **Scaleway** | Serverless Containers | **75k GB-sec/mo** | Pay-as-you-go |
| **Fleek** | Web3 Static Frontend | **Decentralized CDN / SSL** | $20/mo |
| **Stormkit** | JS Frontend Hosting | **50 GB Bandwidth/mo** | $15/mo |
| **YugabyteDB** | Distributed Postgres | **2 vCPU / 4 GB RAM / 10 GB Storage** | Pay-as-you-go |
| **QuestDB** | Time-Series SQL | **Trial credits** | $0.08/hr |
| **Internet Computer** | Decentralized WASM Backends | **Free startup cycles** | Usage-based (cycles) |

That pretty much exhausts the mainstream, alternative, edge, and niche landscape for hosting platforms across backends, frontends, and databases!

If we push any further into the edges of infrastructure, we enter **five ultra-niche domains**:

---

### **1. Bare-Metal, Micro-VMs & Unmanaged Micro-Hosts**

* **Fly.io Machine API & Firecracker:** Running raw AWS Firecracker micro-VMs programmatically via API for ephemeral background jobs.
* **SupaSystems / Serv00 / Ct8.pl:** Legacy free shell-account hosting providers (mostly European non-profits offering raw SSH access, persistent Cron jobs, and low-spec background processes).

### **2. Self-Hosted Tunneling & Local-to-Cloud Runtime**

*Instead of hosting code on someone else's server, you run it on your local machine, a Raspberry Pi, or a home server and expose it securely to the web for free.*

* **Cloudflare Tunnels (cloudflared):** Expose local ports (backend/frontend/database) to the internet with custom domains, free SSL, and zero open ports on your router.
* **ngrok / localtunnel / zrok:** Ephemeral or persistent tunneling services with developer tiers for webhooks and API endpoints.

### **3. Specialized Mobile & Real-Time Sync Backends**

* **Convex:** A reactive backend-as-a-service (BaaS) providing real-time database state sync, background functions, and file storage with a generous always-free tier.
* **InstantDB / Replicache:** Real-time client-side databases that handle automatic synchronization to relational backends.

### **4. Autonomous AI Agent & Scraping Hosts**

* **Browserless.io:** Cloud-hosted headless Chrome browser instances for automated web scraping, PDF generation, and AI browser actions (free tier offers 1,000 sessions/month).
* **Apify:** Serverless runtime built specifically for running web crawlers, scrapers, and automation actors (includes $5/month recurring free credit).

### **5. Peer-to-Peer & Decentralized Compute**

* **Akash Network:** A decentralized cloud compute marketplace (Kubernetes on open provider hardware) where running continuous containers often costs ~70–80% less than traditional cloud platforms.
* **Flux Network:** Decentralized Web3 infrastructure for hosting Docker containers, static sites, and nodes across a globally distributed network.

---



