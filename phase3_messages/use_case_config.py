"""
Comprehensive Use Case Configuration
Maps company verticals to detailed use cases with priority levels and title relevance.
Merges production use cases (Tier 1) with adjacent/research use cases (Tier 2).
"""

from typing import List, Dict, TypedDict


class UseCase(TypedDict):
    """Structure for a single use case"""
    name: str
    description: str
    priority: int  # 1 = production/built, 2 = adjacent/future
    relevant_titles: List[str]  # Keywords for title matching


class ValueProp(TypedDict):
    """Structure for a value proposition"""
    text: str
    relevant_titles: List[str]  # Keywords for title matching


class VerticalConfig(TypedDict):
    """Configuration for a vertical/industry"""
    name: str
    use_cases: List[UseCase]
    value_props: List[ValueProp]


# Comprehensive vertical configuration
VERTICAL_CONFIG: Dict[str, VerticalConfig] = {
    "carrier": {
        "name": "Carrier (Trucking - FTL/LTL)",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "inbound shipper sales",
                "description": "AI-powered inbound sales automation for new shipper acquisition and quote management",
                "priority": 1,
                "relevant_titles": ["sales", "revenue", "growth", "commercial", "business development"]
            },
            {
                "name": "outbound carrier sales",
                "description": "Automated carrier outreach for capacity sourcing and backhaul opportunities",
                "priority": 1,
                "relevant_titles": ["sales", "capacity", "network", "operations"]
            },
            {
                "name": "driver recruiting",
                "description": "Automated screening, outreach, qualification, interview scheduling, after-hours lead capture, and orientation/compliance reminders to combat 85-90% driver turnover",
                "priority": 1,
                "relevant_titles": ["recruiting", "talent", "hr", "workforce", "driver"]
            },
            {
                "name": "customer support",
                "description": "AI-powered contact center automation for shipment status, tracking updates, and routine inquiries",
                "priority": 1,
                "relevant_titles": ["customer", "support", "service", "experience", "contact center"]
            },
            {
                "name": "shipment tracking",
                "description": "Automated tracking updates and proactive delay notifications to shippers and customers",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "technology", "visibility", "tracking"]
            },
            {
                "name": "appointment scheduling",
                "description": "Automated dock scheduling and appointment coordination with warehouses and facilities",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "scheduling", "coordination"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "route optimization",
                "description": "AI-driven routing to reduce fuel costs and optimize driver utilization",
                "priority": 2,
                "relevant_titles": ["operations", "technology", "efficiency", "optimization", "sustainability"]
            },
            {
                "name": "fleet maintenance",
                "description": "Predictive maintenance to minimize breakdowns and extend equipment life",
                "priority": 2,
                "relevant_titles": ["operations", "fleet", "maintenance", "asset", "technology"]
            },
            {
                "name": "hours of service compliance",
                "description": "Automated ELD tracking and regulatory compliance monitoring",
                "priority": 2,
                "relevant_titles": ["compliance", "safety", "operations", "technology"]
            },
            {
                "name": "freight matching",
                "description": "Access to digital marketplaces to find backhaul opportunities and reduce deadhead miles",
                "priority": 2,
                "relevant_titles": ["operations", "technology", "network", "optimization"]
            }
        ],
        "value_props": [
            {
                "text": "reduce driver turnover costs by 40% with AI-powered recruiting automation",
                "relevant_titles": ["recruiting", "talent", "hr", "workforce", "driver", "operations"]
            },
            {
                "text": "increase fleet utilization by 25% through intelligent load matching and backhaul optimization",
                "relevant_titles": ["operations", "fleet", "network", "optimization", "efficiency"]
            },
            {
                "text": "cut fuel costs by 15-20% with AI-driven route optimization",
                "relevant_titles": ["operations", "efficiency", "optimization", "finance", "sustainability"]
            },
            {
                "text": "handle 3x customer inquiry volume without adding headcount",
                "relevant_titles": ["customer", "support", "service", "operations", "contact center"]
            },
            {
                "text": "reduce manual dispatch work by 70% with automated scheduling and tracking",
                "relevant_titles": ["operations", "dispatch", "logistics", "technology", "automation"]
            },
            {
                "text": "improve on-time performance with proactive delay detection and customer communication",
                "relevant_titles": ["operations", "customer", "service", "technology", "visibility"]
            }
        ]
    },

    "freight_broker": {
        "name": "Freight Broker",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "inbound shipper sales",
                "description": "AI-powered inbound sales automation for quote requests, RFQs, and new shipper acquisition",
                "priority": 1,
                "relevant_titles": ["sales", "revenue", "growth", "commercial", "business development"]
            },
            {
                "name": "outbound carrier sales",
                "description": "Automated carrier outreach, vetting, and relationship management for capacity sourcing",
                "priority": 1,
                "relevant_titles": ["sales", "carrier", "capacity", "procurement", "operations"]
            },
            {
                "name": "outbound load booking",
                "description": "Automated load posting, carrier matching, and booking confirmation",
                "priority": 1,
                "relevant_titles": ["operations", "sales", "brokerage", "logistics"]
            },
            {
                "name": "carrier collections calls",
                "description": "Automated payment status updates and collections outreach to carriers",
                "priority": 1,
                "relevant_titles": ["operations", "finance", "collections", "carrier"]
            },
            {
                "name": "shipment tracking",
                "description": "Real-time shipment tracking, proactive delay notifications, and customer communication",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "technology", "visibility"]
            },
            {
                "name": "driver recruiting",
                "description": "Automated driver screening, outreach, qualification, and interview scheduling for capacity building",
                "priority": 1,
                "relevant_titles": ["recruiting", "talent", "hr", "workforce", "driver", "capacity"]
            },
            {
                "name": "LTL inbound customer support",
                "description": "AI-powered contact center for LTL shipment inquiries, pickup requests, and rate quotes",
                "priority": 1,
                "relevant_titles": ["customer", "support", "service", "ltl", "contact center"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "automated load matching",
                "description": "AI-powered matching of available freight with qualified carriers to reduce manual search time",
                "priority": 2,
                "relevant_titles": ["technology", "operations", "automation", "innovation"]
            },
            {
                "name": "dynamic pricing",
                "description": "Real-time pricing algorithms based on market conditions, capacity, and lane history",
                "priority": 2,
                "relevant_titles": ["pricing", "revenue", "strategy", "analytics", "technology"]
            },
            {
                "name": "carrier vetting",
                "description": "Automated verification of carrier credentials, insurance, and fraud detection (double brokering prevention)",
                "priority": 2,
                "relevant_titles": ["compliance", "risk", "operations", "technology"]
            },
            {
                "name": "touchless freight booking",
                "description": "API-based rate requests and booking automation for shipper self-service",
                "priority": 2,
                "relevant_titles": ["technology", "digital", "innovation", "customer"]
            }
        ],
        "value_props": [
            {
                "text": "increase carrier connection rates by 60% with AI-powered outbound dialing",
                "relevant_titles": ["sales", "carrier", "capacity", "operations", "procurement"]
            },
            {
                "text": "reduce manual load matching time by 70% with intelligent automation",
                "relevant_titles": ["operations", "brokerage", "logistics", "technology", "automation"]
            },
            {
                "text": "handle 5x quote volume without adding sales headcount",
                "relevant_titles": ["sales", "revenue", "growth", "commercial", "business development"]
            },
            {
                "text": "improve margin by 3-5 points through dynamic pricing and market intelligence",
                "relevant_titles": ["pricing", "revenue", "finance", "strategy", "analytics"]
            },
            {
                "text": "cut carrier vetting time from hours to minutes with automated compliance checks",
                "relevant_titles": ["compliance", "risk", "operations", "carrier", "technology"]
            },
            {
                "text": "scale brokerage operations 10x without proportional headcount growth",
                "relevant_titles": ["operations", "growth", "strategy", "technology", "efficiency"]
            }
        ]
    },

    "3pl": {
        "name": "3PL/4PL/Forwarder",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "inbound sales",
                "description": "AI-powered lead qualification, quote management, and RFQ automation for new customer acquisition",
                "priority": 1,
                "relevant_titles": ["sales", "revenue", "growth", "commercial", "business development"]
            },
            {
                "name": "customer support",
                "description": "Multi-channel contact center automation for shipment status, inventory queries, and routine requests",
                "priority": 1,
                "relevant_titles": ["customer", "support", "service", "experience", "contact center"]
            },
            {
                "name": "appointment scheduling",
                "description": "Automated dock scheduling, appointment coordination, and facility management across warehouse network",
                "priority": 1,
                "relevant_titles": ["operations", "warehouse", "logistics", "scheduling"]
            },
            {
                "name": "quote management",
                "description": "Automated quote generation, pricing, and proposal management for RFQs",
                "priority": 1,
                "relevant_titles": ["sales", "pricing", "operations", "commercial"]
            },
            {
                "name": "shipment tracking",
                "description": "Real-time shipment tracking, proactive delay notifications, and customer communication",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "technology", "visibility", "tracking"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "warehouse management",
                "description": "Cloud-based WMS coordination to manage inventory visibility across multiple clients and facilities",
                "priority": 2,
                "relevant_titles": ["warehouse", "technology", "operations", "inventory"]
            },
            {
                "name": "transportation management",
                "description": "Centralized platform for managing multi-modal transportation and carrier relationships",
                "priority": 2,
                "relevant_titles": ["transportation", "technology", "operations", "logistics"]
            },
            {
                "name": "supply chain visibility",
                "description": "Real-time dashboards and analytics for clients to track shipments and inventory",
                "priority": 2,
                "relevant_titles": ["technology", "analytics", "visibility", "customer", "data"]
            },
            {
                "name": "reverse logistics",
                "description": "Efficient processing of returns, refurbishment, and disposition management",
                "priority": 2,
                "relevant_titles": ["operations", "warehouse", "customer", "ecommerce"]
            },
            {
                "name": "demand forecasting",
                "description": "AI-driven forecasting to optimize inventory positioning and capacity planning",
                "priority": 2,
                "relevant_titles": ["analytics", "technology", "strategy", "innovation", "data"]
            }
        ],
        "value_props": [
            {
                "text": "handle 4x customer inquiry volume without expanding contact center headcount",
                "relevant_titles": ["customer", "support", "service", "operations", "contact center"]
            },
            {
                "text": "reduce dock scheduling conflicts by 80% with intelligent appointment automation",
                "relevant_titles": ["operations", "warehouse", "logistics", "scheduling", "coordination"]
            },
            {
                "text": "increase quote conversion rate by 35% with instant, accurate RFQ responses",
                "relevant_titles": ["sales", "revenue", "growth", "commercial", "pricing"]
            },
            {
                "text": "improve customer retention with real-time visibility and proactive communication",
                "relevant_titles": ["customer", "account management", "technology", "visibility", "operations"]
            },
            {
                "text": "cut operational costs by 30-40% through AI-powered workflow automation",
                "relevant_titles": ["operations", "finance", "efficiency", "technology", "automation"]
            },
            {
                "text": "scale multi-client operations without proportional staffing increases",
                "relevant_titles": ["operations", "growth", "strategy", "technology", "efficiency"]
            }
        ]
    },

    "ocean_carrier": {
        "name": "Ocean Carrier",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "customer care automation",
                "description": "AI-powered support for container status, holds and releases, last free day, and charges inquiries",
                "priority": 1,
                "relevant_titles": ["customer", "support", "service", "experience", "contact center"]
            },
            {
                "name": "shipment tracking",
                "description": "Real-time container tracking, vessel status updates, and automated customer notifications",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "technology", "visibility"]
            },
            {
                "name": "container releases",
                "description": "Automated processing of container holds, releases, and documentation coordination",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "documentation", "compliance"]
            },
            {
                "name": "demurrage monitoring",
                "description": "Proactive outreach to reduce fees, automated notifications for free time expiration",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "revenue", "finance"]
            },
            {
                "name": "terminal coordination",
                "description": "Appointment scheduling, pre-arrival coordination, and terminal communication automation",
                "priority": 1,
                "relevant_titles": ["operations", "terminal", "coordination", "logistics"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "digital documentation",
                "description": "E-bills of lading and automated customs documentation to reduce paper processes",
                "priority": 2,
                "relevant_titles": ["technology", "digital", "innovation", "operations"]
            },
            {
                "name": "port congestion management",
                "description": "AI-driven planning to optimize vessel schedules and reduce port delays",
                "priority": 2,
                "relevant_titles": ["operations", "planning", "analytics", "technology"]
            },
            {
                "name": "vessel scheduling",
                "description": "Dynamic route planning and capacity allocation based on demand forecasting",
                "priority": 2,
                "relevant_titles": ["operations", "planning", "analytics", "network"]
            }
        ],
        "value_props": [
            {
                "text": "reduce detention and demurrage fees by 40% with proactive customer outreach",
                "relevant_titles": ["operations", "customer", "revenue", "finance", "terminal"]
            },
            {
                "text": "handle 5x customer inquiry volume without expanding service center teams",
                "relevant_titles": ["customer", "support", "service", "operations", "contact center"]
            },
            {
                "text": "improve container release processing time by 60% with automated workflows",
                "relevant_titles": ["operations", "documentation", "compliance", "technology", "automation"]
            },
            {
                "text": "cut terminal coordination overhead by 70% through intelligent scheduling",
                "relevant_titles": ["operations", "terminal", "coordination", "logistics", "technology"]
            },
            {
                "text": "increase customer satisfaction scores with real-time visibility and proactive updates",
                "relevant_titles": ["customer", "service", "technology", "visibility", "operations"]
            },
            {
                "text": "reduce manual documentation processing time by 80% with digital transformation",
                "relevant_titles": ["operations", "technology", "digital", "documentation", "automation"]
            }
        ]
    },

    "air_freight": {
        "name": "Air Freight & Commercial Airlines",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "cargo sales automation",
                "description": "RFQ automation, quote generation, and booking management for cargo capacity",
                "priority": 1,
                "relevant_titles": ["sales", "cargo", "revenue", "commercial"]
            },
            {
                "name": "shipment tracking",
                "description": "Real-time airway bill tracking, flight status updates, and delivery notifications",
                "priority": 1,
                "relevant_titles": ["operations", "customer", "tracking", "visibility"]
            },
            {
                "name": "capacity search",
                "description": "Automated capacity search and availability confirmation for cargo bookings",
                "priority": 1,
                "relevant_titles": ["operations", "sales", "cargo", "capacity"]
            },
            {
                "name": "contact center automation",
                "description": "AI-powered prioritization of inbound requests across voice and email channels",
                "priority": 1,
                "relevant_titles": ["customer", "support", "service", "contact center"]
            },

            # TIER 2 - Adjacent/future use cases (passenger operations)
            {
                "name": "disruption rebooking",
                "description": "Automated passenger rebooking for flight cancellations and delays",
                "priority": 2,
                "relevant_titles": ["operations", "customer", "passenger", "service"]
            },
            {
                "name": "baggage support",
                "description": "Lost baggage tracking, claims processing, and customer communication",
                "priority": 2,
                "relevant_titles": ["customer", "service", "operations", "support"]
            },
            {
                "name": "capacity management",
                "description": "Real-time access to available cargo space on passenger and cargo flights",
                "priority": 2,
                "relevant_titles": ["cargo", "capacity", "revenue", "operations"]
            },
            {
                "name": "customs clearance",
                "description": "Expedited processing of international shipment documentation and compliance",
                "priority": 2,
                "relevant_titles": ["compliance", "operations", "customs", "international"]
            }
        ],
        "value_props": [
            {
                "text": "increase cargo quote conversion by 45% with instant RFQ automation",
                "relevant_titles": ["sales", "cargo", "revenue", "commercial", "pricing"]
            },
            {
                "text": "handle 6x passenger inquiry volume during disruptions without adding staff",
                "relevant_titles": ["customer", "support", "service", "operations", "passenger"]
            },
            {
                "text": "reduce baggage claim resolution time by 50% with AI-powered case management",
                "relevant_titles": ["customer", "service", "operations", "support", "passenger"]
            },
            {
                "text": "improve cargo utilization by 20% through intelligent capacity management",
                "relevant_titles": ["cargo", "capacity", "revenue", "operations", "optimization"]
            },
            {
                "text": "cut manual booking time by 70% with automated availability search and confirmation",
                "relevant_titles": ["operations", "sales", "cargo", "technology", "automation"]
            },
            {
                "text": "enhance customer satisfaction with real-time tracking and proactive communication",
                "relevant_titles": ["customer", "service", "technology", "visibility", "operations"]
            }
        ]
    },

    "food_distributor": {
        "name": "Food Distributor",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "order updates",
                "description": "Voice AI agent for real-time order modifications, product substitutions, and urgent requests",
                "priority": 1,
                "relevant_titles": ["customer", "service", "operations", "sales"]
            },
            {
                "name": "appointment scheduling",
                "description": "Automated delivery window coordination and warehouse dock scheduling",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "warehouse", "transportation"]
            },
            {
                "name": "supplier outreach",
                "description": "Automated procurement communication, order confirmations, and vendor coordination",
                "priority": 1,
                "relevant_titles": ["procurement", "supply chain", "operations", "sourcing"]
            },
            {
                "name": "document collection",
                "description": "Automated proof of delivery collection and invoice processing",
                "priority": 1,
                "relevant_titles": ["operations", "finance", "accounting", "logistics"]
            },
            {
                "name": "temperature monitoring",
                "description": "Real-time cold chain monitoring with automated alerts for temperature excursions",
                "priority": 1,
                "relevant_titles": ["operations", "quality", "compliance", "food safety"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "customer support",
                "description": "AI-powered contact center for order status, product availability, and account inquiries",
                "priority": 2,
                "relevant_titles": ["customer", "service", "support", "contact center"]
            },
            {
                "name": "inventory tracking",
                "description": "Real-time stock level updates and automated out-of-stock notifications",
                "priority": 2,
                "relevant_titles": ["inventory", "warehouse", "operations", "technology"]
            }
        ],
        "value_props": [
            {
                "text": "reduce order change processing time by 80% with voice AI automation",
                "relevant_titles": ["customer", "service", "operations", "technology", "automation"]
            },
            {
                "text": "eliminate dock scheduling conflicts and improve delivery window accuracy",
                "relevant_titles": ["operations", "logistics", "warehouse", "transportation", "scheduling"]
            },
            {
                "text": "cut POD collection time from days to hours with automated follow-up",
                "relevant_titles": ["operations", "finance", "accounting", "logistics", "automation"]
            },
            {
                "text": "prevent spoilage and compliance issues with real-time temperature monitoring",
                "relevant_titles": ["operations", "quality", "compliance", "food safety", "technology"]
            },
            {
                "text": "handle 4x customer order volume without expanding service team",
                "relevant_titles": ["customer", "service", "support", "operations", "growth"]
            },
            {
                "text": "improve supplier relationship management with consistent, timely communication",
                "relevant_titles": ["procurement", "supply chain", "operations", "sourcing", "vendor"]
            }
        ]
    },

    "shipper": {
        "name": "Shipper/Manufacturer",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "appointment scheduling",
                "description": "Automated dock scheduling and carrier appointment coordination for inbound/outbound shipments",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "warehouse", "transportation"]
            },
            {
                "name": "carrier communication",
                "description": "Automated status updates, check calls, and carrier coordination for pickups and deliveries",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "transportation", "supply chain"]
            },
            {
                "name": "shipment tracking",
                "description": "Real-time visibility and proactive delay notifications for inbound materials and outbound finished goods",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "supply chain", "visibility"]
            },
            {
                "name": "claims processing",
                "description": "Automated freight claim filing, documentation collection, and resolution tracking",
                "priority": 1,
                "relevant_titles": ["operations", "logistics", "finance", "risk"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "supply chain visibility",
                "description": "End-to-end tracking of inbound materials and outbound finished goods across the network",
                "priority": 2,
                "relevant_titles": ["supply chain", "technology", "visibility", "operations"]
            },
            {
                "name": "transportation procurement",
                "description": "RFP automation and contract management with carriers",
                "priority": 2,
                "relevant_titles": ["procurement", "logistics", "transportation", "strategy"]
            },
            {
                "name": "inventory optimization",
                "description": "AI-driven demand forecasting to reduce carrying costs and improve service levels",
                "priority": 2,
                "relevant_titles": ["supply chain", "planning", "analytics", "inventory"]
            },
            {
                "name": "supplier collaboration",
                "description": "EDI and API connections for automated PO and ASN processing",
                "priority": 2,
                "relevant_titles": ["technology", "supply chain", "procurement", "integration"]
            }
        ],
        "value_props": [
            {
                "text": "eliminate dock scheduling conflicts and reduce carrier wait time by 60%",
                "relevant_titles": ["operations", "logistics", "warehouse", "transportation", "scheduling"]
            },
            {
                "text": "cut manual carrier check-call time by 80% with automated status updates",
                "relevant_titles": ["operations", "logistics", "transportation", "automation", "technology"]
            },
            {
                "text": "reduce freight claim processing time from weeks to days",
                "relevant_titles": ["operations", "logistics", "finance", "risk", "transportation"]
            },
            {
                "text": "improve on-time delivery performance with proactive delay management",
                "relevant_titles": ["operations", "logistics", "supply chain", "customer", "visibility"]
            },
            {
                "text": "gain end-to-end supply chain visibility without complex IT integration",
                "relevant_titles": ["supply chain", "technology", "visibility", "operations", "innovation"]
            },
            {
                "text": "scale shipping operations 3x without adding logistics headcount",
                "relevant_titles": ["operations", "logistics", "growth", "efficiency", "technology"]
            }
        ]
    },

    "warehousing": {
        "name": "Warehousing/Distribution Center",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "appointment scheduling",
                "description": "Automated dock door scheduling, carrier appointment management, and yard coordination",
                "priority": 1,
                "relevant_titles": ["operations", "warehouse", "logistics", "yard"]
            },
            {
                "name": "customer support",
                "description": "AI-powered contact center for inventory status, order updates, and inbound inquiries",
                "priority": 1,
                "relevant_titles": ["customer", "service", "support", "contact center"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "warehouse management",
                "description": "Automated inventory tracking, slotting optimization, and labor management coordination",
                "priority": 2,
                "relevant_titles": ["warehouse", "technology", "operations", "inventory", "wms"]
            },
            {
                "name": "labor scheduling",
                "description": "Workforce planning, productivity tracking, and temp labor coordination",
                "priority": 2,
                "relevant_titles": ["operations", "workforce", "labor", "hr", "scheduling"]
            },
            {
                "name": "yard management",
                "description": "Trailer tracking, dock door optimization, and detention reduction",
                "priority": 2,
                "relevant_titles": ["operations", "yard", "logistics", "transportation"]
            },
            {
                "name": "inventory accuracy",
                "description": "RFID and barcode scanning coordination for real-time inventory reconciliation",
                "priority": 2,
                "relevant_titles": ["warehouse", "inventory", "operations", "accuracy"]
            },
            {
                "name": "returns processing",
                "description": "Efficient handling of damaged, returned, or refurbished goods",
                "priority": 2,
                "relevant_titles": ["operations", "warehouse", "reverse logistics", "ecommerce"]
            }
        ],
        "value_props": [
            {
                "text": "reduce dock scheduling conflicts by 85% with intelligent appointment automation",
                "relevant_titles": ["operations", "warehouse", "logistics", "yard", "scheduling"]
            },
            {
                "text": "handle 5x customer inquiry volume without expanding warehouse office teams",
                "relevant_titles": ["customer", "service", "support", "operations", "warehouse"]
            },
            {
                "text": "cut yard dwell time by 40% with automated trailer tracking and door assignment",
                "relevant_titles": ["operations", "yard", "logistics", "transportation", "technology"]
            },
            {
                "text": "improve inventory accuracy from 95% to 99.5% with real-time reconciliation",
                "relevant_titles": ["warehouse", "inventory", "operations", "accuracy", "technology"]
            },
            {
                "text": "reduce labor scheduling overhead by 60% with AI-powered workforce planning",
                "relevant_titles": ["operations", "workforce", "labor", "hr", "scheduling"]
            },
            {
                "text": "scale warehouse operations without proportional administrative headcount growth",
                "relevant_titles": ["operations", "warehouse", "growth", "efficiency", "technology"]
            }
        ]
    },

    "customs_broker": {
        "name": "Customs Broker",
        "use_cases": [
            # TIER 1 - Production use cases
            {
                "name": "customer support",
                "description": "AI-powered contact center for clearance status, documentation requirements, and inquiry handling",
                "priority": 1,
                "relevant_titles": ["customer", "service", "support", "contact center"]
            },

            # TIER 2 - Adjacent/future use cases
            {
                "name": "document processing",
                "description": "OCR and AI extraction of data from commercial invoices and packing lists",
                "priority": 2,
                "relevant_titles": ["technology", "operations", "automation", "documentation"]
            },
            {
                "name": "tariff classification",
                "description": "AI-powered tariff code assignment for accurate duty calculation",
                "priority": 2,
                "relevant_titles": ["compliance", "operations", "classification", "technology"]
            },
            {
                "name": "compliance monitoring",
                "description": "Screening shipments against denied party lists and trade regulations",
                "priority": 2,
                "relevant_titles": ["compliance", "risk", "security", "operations"]
            },
            {
                "name": "customs clearance",
                "description": "Electronic submission to CBP and other customs authorities with automated validation",
                "priority": 2,
                "relevant_titles": ["operations", "customs", "compliance", "technology"]
            },
            {
                "name": "duty drawback management",
                "description": "Tracking and filing for refunds on re-exported goods",
                "priority": 2,
                "relevant_titles": ["finance", "compliance", "operations", "revenue"]
            }
        ],
        "value_props": [
            {
                "text": "handle 6x customer inquiry volume without expanding brokerage service teams",
                "relevant_titles": ["customer", "service", "support", "operations", "contact center"]
            },
            {
                "text": "reduce document processing time by 75% with AI-powered OCR and extraction",
                "relevant_titles": ["operations", "technology", "automation", "documentation", "compliance"]
            },
            {
                "text": "improve classification accuracy and reduce duty assessment errors by 90%",
                "relevant_titles": ["compliance", "operations", "classification", "technology", "risk"]
            },
            {
                "text": "cut customs clearance processing time from hours to minutes",
                "relevant_titles": ["operations", "customs", "compliance", "technology", "efficiency"]
            },
            {
                "text": "automate compliance screening to prevent costly violations and delays",
                "relevant_titles": ["compliance", "risk", "security", "operations", "technology"]
            },
            {
                "text": "scale brokerage operations 5x without proportional headcount increases",
                "relevant_titles": ["operations", "growth", "strategy", "technology", "efficiency"]
            }
        ]
    }
}


def get_vertical_config(vertical_key: str) -> VerticalConfig:
    """
    Get configuration for a specific vertical.

    Args:
        vertical_key: The vertical identifier (e.g., 'carrier', 'freight_broker')

    Returns:
        VerticalConfig dictionary with name, use_cases, and value_props
    """
    return VERTICAL_CONFIG.get(vertical_key, VERTICAL_CONFIG["carrier"])


def get_all_vertical_keys() -> List[str]:
    """Get list of all available vertical keys."""
    return list(VERTICAL_CONFIG.keys())


def get_all_vertical_names() -> List[Dict[str, str]]:
    """Get list of all verticals with keys and display names."""
    return [
        {"key": key, "name": config["name"]}
        for key, config in VERTICAL_CONFIG.items()
    ]
