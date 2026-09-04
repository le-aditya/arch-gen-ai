export const mockInput = {
  description: "I want to build an online food delivery platform where customers can browse restaurants, order food, make payments and track delivery in real-time.",
  team_size: 4,
  budget: "low",
  expected_users: "medium",
  availability: "high"
}

export const mockRequirements = {
  domain: "food_delivery",
  actors: ["customer", "restaurant", "delivery_partner", "admin"],
  modules: [
    "registration",
    "restaurant_browsing",
    "ordering",
    "payment",
    "tracking",
    "notifications"
  ],
  real_time: true,
  payment: true,
  external_integrations: ["maps", "payment_gateway", "sms"],
  data_complexity: "high"
}

export const mockPrediction = {
  architecture: "Microservices",
  confidence: 0.84,
  top_factors: [
    { name: "Real-time requirement", importance: 0.28 },
    { name: "Number of modules", importance: 0.22 },
    { name: "External integrations", importance: 0.18 },
    { name: "Availability requirement", importance: 0.15 },
    { name: "Data complexity", importance: 0.12 }
  ]
}

export const mockArchitecture = {
  tech_stack: {
    frontend: ["React", "TypeScript"],
    backend: ["Node.js", "Express"],
    database: ["PostgreSQL", "Redis"],
    messaging: ["RabbitMQ"],
    infrastructure: ["Docker", "Nginx"]
  },
  database: {
    tables: [
      {
        name: "Customer",
        columns: ["customer_id PK", "name", "email", "phone", "created_at"]
      },
      {
        name: "Restaurant",
        columns: ["restaurant_id PK", "name", "cuisine_type", "address", "is_active"]
      },
      {
        name: "Order",
        columns: ["order_id PK", "customer_id FK", "restaurant_id FK", "status", "total", "created_at"]
      },
      {
        name: "Payment",
        columns: ["payment_id PK", "order_id FK", "amount", "method", "status", "paid_at"]
      }
    ]
  },
  apis: [
    { method: "POST", path: "/api/auth/register", purpose: "Register new user" },
    { method: "POST", path: "/api/auth/login", purpose: "User login" },
    { method: "GET", path: "/api/restaurants", purpose: "List restaurants" },
    { method: "POST", path: "/api/orders", purpose: "Create new order" },
    { method: "GET", path: "/api/orders/:id/track", purpose: "Track order delivery" },
    { method: "POST", path: "/api/payments", purpose: "Process payment" }
  ],
  diagrams: {
    architecture: "Microservices with API Gateway",
    deployment: "Load Balancer → Docker Containers → PostgreSQL + Redis"
  }
}

export const mockReport = {
  id: "rpt_001",
  created_at: "2026-09-04T10:30:00Z",
  summary: "Food delivery platform recommended for microservices architecture with 84% confidence."
}
