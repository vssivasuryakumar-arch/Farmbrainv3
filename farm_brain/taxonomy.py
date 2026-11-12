"""Initial FARM BRAIN category taxonomy based on the project master brief."""

CATEGORIES = {
    "Agri Products": [
        "Flowers", "Greens", "Vegetables", "Herbs", "Cereals", "Pulses",
        "Millets", "Spices", "Dry Fruits", "Plantation Crops", "Fibre Crops",
        "Forage Crops", "Seeds",
    ],
    "Agri Business": [
        "Factory", "Transport", "Land", "Machineries", "Electrical Components",
        "Tech Career", "Notifications & Updates", "Banks & Investors", "Inventory",
    ],
    "Livestock": [
        "Buy/Sell Livestock", "Livestock Products", "Feeds", "Meat Industry",
        "Veterinarian", "Manures",
    ],
    "Farm Aid": [
        "Seeds", "Saplings", "Farm-made Products", "Components", "Fertilizers",
        "Farm Machinery", "Farm Labour", "Modern Farm", "Learning & Internship",
    ],
}

DIVISIONS = list(CATEGORIES.keys())
RECORD_TYPES = {"offer": "Offer / supply", "requirement": "Requirement / demand"}
CURRENCIES = ["INR", "AED", "USD", "GBP"]
CAPABILITIES = [
    "Farmer / Grower", "Buyer", "Seller / Supplier", "Processor / Factory",
    "Transporter / Vehicle Owner", "Land Owner / Seeker", "Machinery Owner / Seeker",
    "Employer / Recruiter", "Worker / Job Seeker", "Student / Trainee",
    "Veterinarian", "Livestock Keeper", "Agri Consultant", "Investor / Finance Seeker",
    "Community Contributor",
]
TRANSPORT_KINDS = {
    "load_request": "Load request",
    "vehicle_availability": "Vehicle availability",
}
