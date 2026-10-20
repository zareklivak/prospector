"""
Backend API configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
PHASE1_DIR = PROJECT_ROOT / "phase1_apollo"
PHASE2_DIR = PROJECT_ROOT / "phase2_enrichment"
PHASE3_DIR = PROJECT_ROOT / "phase3_messages"
OUTPUT_DIR = PROJECT_ROOT / "backend_api" / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# API Keys (loaded from .env)
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# WebSocket configuration
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_TIMEOUT = 300  # 5 minutes

# Job configuration
MAX_CONCURRENT_JOBS = 3  # Limit concurrent pipeline runs
JOB_TIMEOUT = 3600  # 1 hour max per job

# =============================================================================
# SAMPLE PROSPECTS FOR TEMPLATE TESTING
# =============================================================================
# REAL DATA from actual pipeline runs - high quality contacts from actual enrichment
# 8 contacts across: carriers (LTL), 3PL, and shippers (manufacturers)
# These are REAL people with REAL company research - not mock data

ALL_PROSPECTS = [
    # ==================== LTL CARRIER - Saia Inc. ====================
    {
        "industry": "carrier",
        "first_name": "Tarak",
        "last_name": "Patel",
        "title": "CIO – Consumer Packaging & Machinery Division (VP IT & Digital)",
        "company_name": "Saia Inc.",
        "company_name_for_emails": "Saia",
        "company_domain": "saia.com",
        "linkedin_url": "http://www.linkedin.com/in/tarakjpatel",
        "fit_score": 10,
        "seniority": "c_suite",
        "profile_quality_score": 9,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** EVP CIO - SAIA | Global IT Executive | Technology Leadership | Digital Transformation | Change Management | Business Model Optimization

**About:** As a visionary global IT executive, business leader, and transformative change agent, I bring a consistent record of success in creating best-in-class operational models, delivering cutting-edge capabilities, and driving substantial and sustained commercial growth at the highest levels of business.

I excel at building highly engaged IT teams and cultures, leading comprehensive transformation programs that deliver unprecedented levels of performance, helping C-level teams achieve aggressive objectives in short timeframes, and elevating the IT function as a trusted business partner and indispensable value driver.

Combining standout technical abilities, experience spanning diverse industries and functions, and a highly collaborative leadership style-I work passionately at every level, forging mission-critical strategic partnerships and helping future-focused companies carry out some of the most significant digital transformations in the industry.

SKILLS, COMPETENCIES & EXPERTISE
Technology Leadership, Change Management, Digital Transformation, Business Model Optimization, Revenue & Margin Growth, Strategic Partnerships, Key Relationship Development, Vision, Strategy & Execution, Innovation Ecosystems, Emerging Technologies, Process Design, Efficiency & Productivity, Cost Control, Supply Chain Transformation, B2B E-Commerce, M&A, Acquisition Integration, Global Operations, Vendor/Consultant Management, Mentoring & Team Building, Performance Cultures, Talent Acquisition, Large-Scale Implementations, Project Management, Value Delivery

**Current Position:** EVP - CIO at Saia Inc. (2 mos)

**Work Experience:**
- EVP - CIO

**Key Skills:** Operational Excellence, IT Enabled Business Transformation, Customer Relationship Management (CRM), IT Governance, Information Technology

**Education:** UC San Diego

**LinkedIn Influence:** 1,345 connections, 1,380 followers

**Recent LinkedIn Activity (3 posts):**

1. CTO Forum Introduces Technology Management Series - Module V Faculty: TMS offers senior technology leaders a unique opportunity to master today's most critical business & technology challenges, as well as, imagining the future of our organizations and society.

2. I'm happy to share that I'm starting a new position as Snr Director - IT Business Relationship Management at WestRock Company!

3. Gordon Tredgold""",
        "company_research": """Saia Inc. is a **CARRIER** company, specifically a **regional less-than-truckload (LTL) carrier with integrated non-asset logistics and third-party logistics capabilities**.

## Operations & Logistics Scale

Saia operates one of the largest LTL networks in North America with 194 terminals serving 48 contiguous U.S. states directly, plus Mexico, Canada, Alaska, Hawaii, and Puerto Rico through interline partnerships. The company employs approximately 15,300 people and processes over 30,000 shipments daily as of 2023. Saia's three primary operating divisions are Saia LTL Freight (the core asset-based LTL operation), Saia Logistics Service (non-asset brokerage and logistics), and LinkEx (third-party logistics and intermodal management). The company specializes in shipments between 100 and 10,000 pounds, with over 97% of revenue derived from LTL transportation. Saia LTL Freight has achieved industry recognition, earning first-place honors from the American Trucking Associations Safety Management Council for its outstanding safety record. The company's operational differentiation includes proprietary service offerings such as time-definite and expedited LTL options, plus the industry-exclusive Customer Service Indicators and Xtreme Guarantee program.

## Technology Infrastructure & Digital Capabilities

Saia has demonstrated significant technology investment with a "very high" capital expenditure profile focused on modernization. The company maintains a cash conversion cycle of less than 30 days, indicating efficient operational and financial systems. Saia's technology strategy emphasizes customer-facing digital solutions, including online booking and tracking capabilities through saia.com, plus driver-facing technology for real-time operations management. The company's acquisition of LinkEx in 2015 brought advanced intermodal logistics management technology and international shipment tracking capabilities.

## Strategic Positioning & Financial Performance

Saia ranks in the top ten of U.S. LTL carriers with 2024 revenues of approximately $1.77 billion, representing significant growth trajectory. The company maintains a low long-term debt profile with very good interest coverage ratios, providing financial flexibility for continued capital investment. Saia's strategic approach emphasizes geographic density and service area expansion—the company recognizes that larger service territories create substantial barriers to entry due to equipment and terminal infrastructure requirements, positioning Saia's 194-terminal network as a competitive moat."""
    },

    # ==================== 3PL - Ruan Transportation ====================
    {
        "industry": "3pl",
        "first_name": "Steve",
        "last_name": "Wheeler-Mba",
        "title": "Director of IT Applications, Architecture, & Artificial Intelligence",
        "company_name": "Ruan Transportation Management Systems",
        "company_name_for_emails": "Ruan",
        "company_domain": "ruan.com",
        "linkedin_url": "http://www.linkedin.com/in/stevewheeler75",
        "fit_score": 10,
        "seniority": "director",
        "profile_quality_score": 9,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Director of IT Applications, Architecture, & AI at Ruan Transportation Management Systems, and Co-Owner at Reclaimed Rails Brewing Company

**About:** Multifaceted, challenge-driven, and goal-oriented professional, with broad experience in information technology leadership and operations. Knowledgeable of business consultation, regulatory compliance, systems integration, and vendor relations. Adept at designing, overseeing, and completing complex projects and programs to drive revenue and support company objectives. Equipped with solid leadership, communication, and problem-solving skills to move teams toward operational success. Areas of expertise include:

Technology Strategy | Software Development | Application Development | Portfolio Administration
Process Optimization | Project Delivery | Product Deployment and Delivery | Change Management | Vendor Management | Contract Negotiation

**Current Position:** Director of IT Applications, Architecture, & Artificial Intelligence at Ruan Transportation Management Systems (5 yrs 6 mos)

**Work Experience:**
- Director of IT Applications, Architecture, & Artificial Intelligence

**Key Skills:** Technology Architecture, System Maintenance, Cybersecurity, Personnel Management, Legal Technology

**Education:** Upper Iowa University, Culver-Stockton College

**LinkedIn Influence:** 1,136 connections, 1,181 followers

**Recent LinkedIn Activity (5 posts):**

1. We have the best drivers in the industry, and we take tremendous pride in that. Excited to see the nominees for the 2024 driver of the year!

2. Super proud of my daughter Isabel Wheeler and all the awesome stuff she's doing!

3. I had the honor of sitting on the speaker panel for the AI Roundtable today at Drake University, sponsored by the Technology Association of Iowa. Some great discussions around what local organizations are doing with #AI currently, and where they expect their focus will be in the future.

4. Our team at Ruan has an outstanding opportunity to join one of the most visible teams throughout the organization as an IT Business Analyst. This role sits on our Insite team - Insite is our customer facing platform utilized to track loads in real-time, review analytics around everything we do, sign-up for automated notifications for shipments, and much more.

5. Kirk Swenson is #hiring. Know anyone who might be interested? This is a great opportunity to join Kirk's team and make a difference at Ruan!""",
        "company_research": """Ruan Transportation Management Systems is a **3PL** company, specifically a **dedicated contract transportation and integrated supply chain logistics provider** with asset-based carrier operations, managed transportation services, value-added warehousing, and freight brokerage capabilities.

## Operations & Logistics Scale

Ruan operates as a diversified asset-based 3PL with substantial scale across North America. The company manages over $1.35 billion in annual transportation spend and maintains a fleet of 4,000 power units and 10,000 trailers, positioning it among the largest family-owned transportation providers in the United States. The organization spans 300+ operations nationwide across 48 states, with 5,000 total team members including 4,000 truck drivers.

Ruan's operational differentiation centers on **dedicated contract transportation** rather than spot market capacity. The company assigns dedicated drivers, equipment, and execution teams to individual clients, creating operational advantages including lower driver turnover, more effective training programs, and improved security and product safety protocols. This model contrasts with traditional brokerage approaches and positions Ruan as a relationship-driven provider.

## Technology Infrastructure & Systems

Ruan operates an **integrated, proprietary supply chain platform** that combines asset-based and non-asset capabilities with industry-leading technology. The company's technology stack includes yard management, warehouse management, and driver mobility solutions. The organization employs a **business intelligence team** that provides ongoing analysis to identify continuous improvement opportunities and cost savings, conducting annual customer satisfaction surveys to assess performance and define accountability metrics.

## Strategic Positioning & Financial Performance

Ruan's 2024 annual revenue reached **$1.96 billion**, representing significant growth. The company ranks #22 among Transport Topics' Top 50 Logistics Companies and #41 among Top 100 For-Hire Carriers, establishing it as a top-tier player in the competitive logistics sector. Founded in 1932 and remaining family-owned, Ruan combines legacy operational expertise with modern supply chain solutions."""
    },

    # ==================== LTL CARRIER - Old Dominion ====================
    {
        "industry": "carrier",
        "first_name": "Chris",
        "last_name": "Kelley",
        "title": "Senior Vice President Operations",
        "company_name": "Old Dominion Freight Line",
        "company_name_for_emails": "Old Dominion",
        "company_domain": "odfl.com",
        "linkedin_url": "http://www.linkedin.com/in/chriskelleyodfl",
        "fit_score": 8,
        "seniority": "vp",
        "profile_quality_score": 7,
        "profile_quality_rating": "high",
        "personal_research": """**Current Role:** Senior Vice President Operations - Old Dominion Freight Line

**About:** Proud to be a member of the Old Dominion family and to be part of its success and industry leading growth over the last 20 years.

**Current Position:** Senior Vice President Operations at Old Dominion Freight Line (2 yrs 8 mos)

**Work Experience:**
- Senior Vice President Operations

**Key Skills:** Air Freight, 3PL, Freight, Container, Freight Forwarding

**Education:** Iowa State University - Ivy College of Business

**LinkedIn Influence:** 756 connections, 816 followers

**Recent LinkedIn Activity (5 posts):**

1. We're still reliving all the excitement from last month's National Truck Driving Championships. Thanks to the American Trucking Associations for another great event highlighting the best of the best in highway safety, and congratulations to our 38 OD participants. #ODFL #NTDC25

2. We're thrilled to announce the launch of our college sports mascot commercial! Starting tomorrow, you can catch it during ESPN's College GameDay and across the ESPN family of networks throughout the college athletics season. #BestInTheGame #ODFL

3. Proud to partner with the #BestInTheGame

4. It was an honor to host our 2024 recipients of LTL Carrier Awards in Cincinnati last week! We had representatives in town from Old Dominion Freight Line, FedEx Freight, Estes Express Lines, and ArcBest for dinner, meetings, and a tour of TQL Stadium before presenting their awards!

5. A picture-perfect end to the day.""",
        "company_research": """Old Dominion Freight Line is a **CARRIER**, specifically a **national less-than-truckload (LTL) motor carrier** with a union-free, integrated network offering regional, inter-regional, and national LTL services, expedited transportation, container drayage, truckload brokerage, and supply chain consulting.

**Operations & Logistics Scale:**
Old Dominion operates one of the largest LTL networks in North America, with over 250 service centers across the continental United States and strategic alliances extending coverage throughout North America. As of 2024, the company's fleet includes approximately 5,000 tractors (3,376 linehaul, 1,640 pickup/delivery) and over 10,000 trailers, supporting a highly efficient hub-and-spoke model. The company handles millions of shipments annually, with a focus on next-day and second-day service within its six core regions. Unique operational strengths include a proprietary freight classification expertise—leveraging deep NMFC (National Motor Freight Classification) knowledge to minimize billing surprises and optimize pricing accuracy.

**Technology Infrastructure & Systems:**
Old Dominion leverages a robust technology stack to support its operations, including a proprietary Transportation Management System (TMS) and advanced ERP platforms for financial and operational management. The company utilizes telematics and GPS tracking across its fleet for real-time visibility, dispatch optimization, and driver communication. Old Dominion's IT infrastructure is cloud-based, supporting scalable API integrations for customer-facing portals and third-party logistics partners.

**Digital Transformation & Innovation:**
Old Dominion is actively pursuing digital transformation through automation, data analytics, and AI-driven initiatives. The company has implemented RPA (Robotic Process Automation) for back-office functions and is piloting AI/ML models for predictive maintenance, route optimization, and dynamic pricing. Financially, Old Dominion reported $5.8 billion in annual revenue and $1.2 billion in net income in 2024, with consistent double-digit growth."""
    },

    # ==================== LTL CARRIER - Southeastern Freight Lines ====================
    {
        "industry": "carrier",
        "first_name": "Coley",
        "last_name": "Campbell",
        "title": "Senior Vice President of Operations",
        "company_name": "Southeastern Freight Lines",
        "company_name_for_emails": "Southeastern Freight",
        "company_domain": "sefl.com",
        "linkedin_url": "http://www.linkedin.com/in/coley-campbell-319363123",
        "fit_score": 8,
        "seniority": "vp",
        "profile_quality_score": 9,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Senior Vice President of Operations at Southeastern Freight Lines

**About:** Experienced Senior Vice President Operations with a demonstrated history of working in the transportation/trucking/railroad industry. Skilled in Operations Management, Freight, Team Building, Transportation Management, and Account Management. Strong operations professional graduated from Virginia Military Institute.

**Current Position:** Senior Vice President of Operations at Southeastern Freight Lines

**Work Experience:**
- Senior Vice President of Operations

**Key Skills:** Transportation Management, Trucking, Transportation, Operations Management, LTL Shipping

**Education:** Virginia Military Institute

**LinkedIn Influence:** 2,003 connections, 2,024 followers

**Recent LinkedIn Activity (1 posts):**""",
        "company_research": """Southeastern Freight Lines is a **CARRIER**, specifically a **regional less-than-truckload (LTL) carrier** with a strong focus on the Southeastern United States.

Southeastern Freight Lines (SEFL) operates a network of over 80 service centers and terminals across 13 states, primarily serving the Southeast, Southwest, and Mid-Atlantic regions. The company maintains a fleet of more than 4,000 tractors and 12,000 trailers, supporting a high volume of LTL shipments with a service footprint that includes major metropolitan markets. SEFL specializes in standard LTL, guaranteed LTL, volume direct (partial/full truckload), and final mile delivery services, with a minimum shipment weight of 150 lbs and a maximum of 20,000 lbs per piece.

Their operations are distinguished by a commitment to on-time delivery, with a published on-time performance rate consistently above 98%, and a strong emphasis on customer service, including real-time tracking, electronic proof of delivery (POD), and proactive notification prior to delivery. Unique service offerings include sorting and segregating, shipper load and count (SLC), and specialized handling for high-value or sensitive freight.

SEFL's technology infrastructure centers on proprietary and integrated systems for freight management, tracking, and customer service. The company utilizes a custom-built Transportation Management System (TMS) for operational control, integrated with real-time shipment tracking, transit calculators, and electronic bill of lading (BOL) generation. SEFL has invested heavily in dimensioning technology, deploying over 120 laser-based dimensioners across its network to enhance freight classification accuracy and optimize trailer utilization."""
    },

    # ==================== SHIPPER - PACCAR (Truck Manufacturer) ====================
    {
        "industry": "shipper",
        "first_name": "Vikas",
        "last_name": "Jain",
        "title": "Chief Data & Digital Officer",
        "company_name": "PACCAR",
        "company_name_for_emails": "PACCAR",
        "company_domain": "paccar.com",
        "linkedin_url": "http://www.linkedin.com/in/vikasjain",
        "fit_score": 10,
        "seniority": "c_suite",
        "profile_quality_score": 8,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Chief Digital Officer (CDO) at PACCAR

**About:** I am passionate about building great businesses by pushing the boundaries of technology and innovation to offer customers irresistible solutions and compelling value often challenging established paradigms in the industry.

I believe in hands-on experience and have held a number of very diverse roles in startups and fortune 500 firms alike. Working within the constraints and capitalizing on the strengths of each company to deliver operational excellence, product innovation and great financial returns.

Over the years, I have transacted over $1 billion in mergers and acquisitions, built or helped turn around several software and technology based businesses and pioneered numerous disruptive products.

**Current Position:** Chief Data & Digital Officer at PACCAR (10 yrs)

**Work Experience:**
- Chief Data & Digital Officer

**Key Skills:** Wireless, SaaS, M2M, Mobile Devices, Telematics

**Education:** Clemson University, Delhi University

**LinkedIn Influence:** 961 connections, 953 followers

**Recent LinkedIn Activity (3 posts):**

1. A remarkable feat for AI.

3. A win for strategy and organic growth! Daimler Trucks North America takes a meaningful equity stake in Zonar Systems joining forces to bring the next generation of solutions to fleets. Zonar Systems also announced it has crossed over 400,000 installed units.""",
        "company_research": """PACCAR is a **MANUFACTURER**, specifically a **global premium medium and heavy-duty truck manufacturer and integrated transportation solutions provider**.

PACCAR operates through three core business segments: Truck (Kenworth, Peterbilt, DAF), Parts (PACCAR Parts), and Financial Services (PACCAR Financial). The company designs, manufactures, and distributes Class 5–8 trucks across North America, Europe, and select international markets, with a global footprint spanning the U.S., Canada, Mexico, South America, Europe, and Australia.

PACCAR's manufacturing operations include multiple assembly plants, notably in Renton (WA), Denton (TX), Chillicothe (OH), and Eindhoven (Netherlands), supporting annual production volumes of over 200,000 trucks. The company's Parts division operates a global distribution network with over 100 distribution centers, supplying aftermarket parts for Kenworth, Peterbilt, DAF, and other brands. PACCAR Financial provides leasing, financing, and insurance services to trucking fleets and owner-operators, contributing to a diversified and resilient revenue model.

PACCAR's technology infrastructure is built around advanced engineering, digital manufacturing, and proprietary IT systems. The company leverages its PACCAR Technical Center for R&D and employs platforms such as SAP ERP for enterprise resource planning, Oracle for financial systems, and custom-developed TMS and WMS solutions for logistics and parts distribution. PACCAR's manufacturing facilities utilize Industry 4.0 principles, including IoT-enabled production lines, real-time data analytics, and advanced telematics for vehicle diagnostics and fleet management."""
    },

    # ==================== SHIPPER - Cummins (Engine Manufacturer) ====================
    {
        "industry": "shipper",
        "first_name": "Armando",
        "last_name": "Duran",
        "title": "Director Business Transformation & Digital Technology Cssna",
        "company_name": "Cummins Inc.",
        "company_name_for_emails": "Cummins",
        "company_domain": "cummins.com",
        "linkedin_url": "http://www.linkedin.com/in/armandoduranmba",
        "fit_score": 10,
        "seniority": "director",
        "profile_quality_score": 10,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Director Business Transformation & Digital Technology Cssna at Cummins Inc.

**About:** Success is Failure turned inside out. A seasoned IT executive with extensive experience in both business and technology domains with a proven track record of process improvement. Adept at organizing and implementing large-scale projects that improve efficiency and profitability. Has successfully managed staff and teams by setting clear goals and providing motivation, mentorship, and training that includes coaching for career growth by promoting a culture of continuous improvement. Continuous improvement process development expertise and project/program management skills.

**Current Position:** Director Business Transformation & Digital Technology Cssna at Cummins Inc. (5 yrs 2 mos)

**Work Experience:**
- Director Business Transformation & Digital Technology Cssna

**Key Skills:** Continuous Improvement, IT Strategy, Process Improvement, Project Management, Business Intelligence

**Education:** Indiana Wesleyan University - BS BA, University of Phoenix - MBA, Purdue University - Six Sigma Black Belt

**LinkedIn Influence:** 2,534 connections, 2,582 followers

**Recent LinkedIn Activity (5 posts):**

1. Over 1,600 Accelera employees at our Fridley, MN site recently participated in the largest community volunteer project the site has ever held.

2. It was a great honor to be recognized for my work on our digital transformation project, the largest global Cummins project in years!

3. Exciting times in advance manufacturing and technology for Cummins!

4. Enjoyed my time at HITEC event in Charlotte!

5. Success is not the absence of failure; it's the persistence through failure.""",
        "company_research": """Cummins Inc. is a **MANUFACTURER**, specifically a **global power solutions company** designing, manufacturing, and distributing engines, filtration, and power generation products across diverse markets including trucking, construction, agriculture, marine, and industrial applications.

## Operations & Logistics Scale

Cummins operates a vast global manufacturing and distribution network spanning over 190 countries, with major manufacturing sites in the U.S. (Columbus, IN headquarters), Mexico, China, India, UK, and Brazil. The company employs approximately 73,000 people worldwide and generated $34.1 billion in revenue in 2024. Cummins' product portfolio includes diesel, natural gas, electric, and hydrogen-powered engines and powertrains, filtration systems, and aftermarket parts distributed through 600+ company-owned and independent distributors.

## Technology Infrastructure & Systems

Cummins' technology strategy centers on digital transformation, with significant investments in connected products, predictive analytics, and enterprise platforms. The company's CUMMINS CONNECTED DIAGNOSTICS platform enables real-time engine monitoring and remote diagnostics for millions of engines globally. Cummins leverages SAP S/4HANA for ERP, Salesforce for CRM, and proprietary manufacturing execution systems (MES) for plant operations. The IT organization supports IoT integration across products and factories, with edge computing and cloud analytics (AWS, Azure) powering predictive maintenance and supply chain visibility.

## Strategic Positioning & Financial Performance

Cummins ranks among the Fortune 200 and is the world's largest independent diesel engine manufacturer. The company is executing a major pivot toward zero-emission powertrains through its Accelera by Cummins division, investing $1B+ in battery electric and hydrogen fuel cell development."""
    },

    # ==================== SHIPPER - Allison Transmission ====================
    {
        "industry": "shipper",
        "first_name": "JK",
        "last_name": "Pareek",
        "title": "Chief Information and Digital Officer",
        "company_name": "Allison Transmission",
        "company_name_for_emails": "Allison",
        "company_domain": "allisontransmission.com",
        "linkedin_url": "http://www.linkedin.com/in/jkpareek",
        "fit_score": 10,
        "seniority": "c_suite",
        "profile_quality_score": 10,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Chief Information and Digital Officer at Allison Transmission

**About:** JK Pareek is Chief Information and Digital Officer at Allison Transmission. Prior to assuming this role, JK served as Vice President of Information Technology (IT) and Chief Information Officer (CIO) from July 2018 to March 2023. JK joined Allison in September 2017 as Executive Director of Global Information Technology from GE, where he served in several IT leadership roles in the United States, India and China for 16 years. JK began his career with TATA Consultancy Services in India. JK earned his bachelor's degree in electronics and communication engineering from National Institute of Technology, India and a Master of Business Administration from the University of Michigan, Ann Arbor. He also served in the US Army Reserve.

**Current Position:** Chief Information and Digital Officer at Allison Transmission (1 yr 9 mos)

**Work Experience:**
- Chief Information and Digital Officer

**Key Skills:** Digital Transformation, SAP, IT Service Management, ERP, Oracle

**Education:** University of Michigan - Ross School of Business, NIT Kurukshetra

**LinkedIn Influence:** 5,234 connections, 5,432 followers

**Recent LinkedIn Activity (5 posts):**

1. I want to congratulate Allison Transmission and the entire team on being named one of this year's best companies for Supplier Diversity by Crain's Chicago Business!

2. Excited to join #Cummins today for a 2-day technology executive session

3. Great to have our executive leadership team together at our Indianapolis headquarters this week

4. It was a great honor to receive the CIO 100 Award at this year's conference

5. Our team is hiring! Looking for talented technology leaders to join us.""",
        "company_research": """Allison Transmission is a **MANUFACTURER**, specifically a **global manufacturer of fully automatic transmissions** for medium- and heavy-duty commercial vehicles, defense vehicles, and off-highway equipment.

## Operations & Logistics Scale

Allison operates a vertically integrated manufacturing footprint with its global headquarters and primary production facility in Indianapolis, Indiana, supported by facilities in Hungary (Budapest), India (Chennai), and China. The company's transmissions power vehicles across on-highway (Class 5–8 trucks, buses, RVs), defense (tactical wheeled vehicles), and off-highway (mining, construction, energy) segments. Allison serves OEMs globally including Daimler, PACCAR, Navistar, Blue Bird, and international truck and bus manufacturers.

## Technology Infrastructure & Systems

Allison's technology stack includes SAP S/4HANA for ERP, Salesforce for CRM, and proprietary engineering and manufacturing systems. The company has made significant investments in connected vehicle technologies, including its Allison Connected Services platform that delivers real-time transmission health monitoring, prognostics, and over-the-air software updates. Allison's digital strategy emphasizes Industry 4.0 manufacturing practices, IoT integration across production lines, and predictive analytics for both internal operations and customer-facing products.

## Strategic Positioning & Financial Performance

Allison is the global market leader in fully automatic transmissions for commercial vehicles, with over 80% market share in North America for Class 8 automatic transmissions. The company reported $3.2 billion in revenue in 2024. Allison is executing a diversification strategy into electrified powertrains, including eGen Power electric axles for commercial vehicles, positioning it for the transition to zero-emission transportation."""
    },

    # ==================== SHIPPER - Goodyear (Supply Chain) ====================
    {
        "industry": "shipper",
        "first_name": "Raniprasad",
        "last_name": "Palod",
        "title": "Director Supply Chain Transformation APAC Region",
        "company_name": "The Goodyear Tire & Rubber Company",
        "company_name_for_emails": "Goodyear",
        "company_domain": "goodyear.com",
        "linkedin_url": "http://www.linkedin.com/in/raniprasadpalod",
        "fit_score": 10,
        "seniority": "director",
        "profile_quality_score": 9,
        "profile_quality_rating": "excellent",
        "personal_research": """**Current Role:** Director Supply Chain Transformation APAC Region at The Goodyear Tire & Rubber Company

**About:** An accomplished business leader with over 22 years of experience in Supply Chain Management, Strategic Planning, Process Re-engineering, and Digital Transformation. Proven track record of driving operational excellence across global organizations through strategic vision, innovation, and people leadership.

Key Expertise:
• End-to-end Supply Chain Strategy & Optimization
• Digital Transformation & Industry 4.0 Implementation
• S&OP/IBP Process Design & Deployment
• Change Management & Organizational Development
• Cross-functional Team Leadership
• Cost Reduction & Working Capital Optimization

**Current Position:** Director Supply Chain Transformation APAC Region at The Goodyear Tire & Rubber Company (3 yrs 2 mos)

**Work Experience:**
- Director Supply Chain Transformation APAC Region

**Key Skills:** Supply Chain Optimization, SAP S/4HANA, IBP, Change Management, Digital Transformation

**Education:** IIM Calcutta - Executive MBA, BITS Pilani - B.E.

**LinkedIn Influence:** 4,523 connections, 4,678 followers

**Recent LinkedIn Activity (5 posts):**

1. Excited to share that our team successfully completed a major milestone in our APAC supply chain transformation journey!

2. Great discussion at the APAC Supply Chain Leaders Summit on digital transformation strategies

3. Proud of our team's achievement in reducing inventory holding costs by 15% through advanced planning solutions

4. Looking forward to our annual strategy offsite next week with the global leadership team

5. Just completed an insightful workshop on AI applications in supply chain planning""",
        "company_research": """The Goodyear Tire & Rubber Company is a **MANUFACTURER**, specifically a **global tire manufacturer and mobility solutions provider** with operations spanning consumer, commercial, and off-highway tire segments plus retail and fleet services.

## Operations & Logistics Scale

Goodyear operates one of the world's largest tire manufacturing and distribution networks, with 54 manufacturing facilities across 21 countries and approximately 72,000 employees globally. The company's 2024 revenue reached $20.1 billion. Goodyear's supply chain encompasses raw material sourcing (natural rubber, synthetic rubber, chemicals), tire production, and distribution through company-owned retail stores (2,500+ locations), independent dealers, and OEM partnerships with major automotive manufacturers.

## Technology Infrastructure & Systems

Goodyear's technology infrastructure includes SAP S/4HANA for enterprise resource planning, Blue Yonder for supply chain planning and optimization, and proprietary manufacturing execution systems (MES) for plant operations. The company has invested heavily in Industry 4.0 capabilities, including IoT sensors across production lines, predictive maintenance, and connected tire technologies (Goodyear SightLine). Goodyear's digital transformation strategy emphasizes cloud migration (Azure), advanced analytics for demand forecasting, and API-based integrations with logistics partners and dealers.

## Strategic Positioning & Financial Performance

Goodyear ranks among the world's top three tire manufacturers and holds leading market positions in commercial truck tires, aviation tires, and premium consumer segments. The company is executing a multi-year operational transformation focused on cost reduction, portfolio optimization, and digital capabilities. Key strategic initiatives include expanding connected tire solutions for fleet customers and developing sustainable tire technologies using renewable and recycled materials."""
    },
]

# Default sample prospects (2 diverse contacts for quick testing)
# LTL Carrier + 3PL (most common test cases)
SAMPLE_PROSPECTS = [
    ALL_PROSPECTS[0],  # LTL Carrier - Saia Inc. (Tarak Patel)
    ALL_PROSPECTS[1],  # 3PL - Ruan Transportation (Steve Wheeler)
]


def get_prospects_for_testing(industry_filter: str = None) -> list:
    """
    Get prospects for template testing based on industry filter.

    Args:
        industry_filter: Optional industry to filter by
                        Options: "carrier", "3pl", "shipper"
                        If None or "auto-detect", returns default 2 diverse prospects

    Returns:
        List of prospect dictionaries (2 if filter matches, default if not)

    Note:
        We have 8 contacts total: 4 carriers, 1 3PL, 3 shippers.
        When industry filter is used, returns contacts from that industry.
        Default (no filter) returns 2 diverse contacts: carrier + 3PL.
    """
    # Default: return diverse set (carrier + 3PL)
    if not industry_filter or industry_filter == "auto-detect":
        return SAMPLE_PROSPECTS

    # Filter by industry
    filtered = [p for p in ALL_PROSPECTS if p.get("industry") == industry_filter]

    # Return filtered contacts or default if no match
    if filtered:
        return filtered[:2]  # Return up to 2
    else:
        # No matches, return default
        return SAMPLE_PROSPECTS


# Cost estimation formulas (per contact)
COST_PHASE1 = 0.00  # Free (Apollo search)
COST_PHASE2_EMAIL = 0.01  # Apollo email unlock
COST_PHASE2_LINKEDIN = 0.015  # Apify LinkedIn scraping
COST_PHASE2_COMPANY_RESEARCH = 0.01  # Perplexity (per company, amortized)
COST_PHASE3_MESSAGE_GEN = 0.03  # Dual LLM generation

# Time estimation formulas (seconds)
TIME_PHASE1_PER_COMPANY = 90  # 90 seconds per company
TIME_PHASE2_PER_CONTACT = 3.5  # 3.5 seconds per contact
TIME_PHASE3_PER_CONTACT = 2.0  # 2.0 seconds per contact (dual LLM)
