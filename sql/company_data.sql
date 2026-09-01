-- Core business database design for a pharmaceutical company
-- Covers: drug information, inventory management, sales records
-- Intended for structured-data retrieval with DeepAgents

CREATE DATABASE IF NOT EXISTS pharma_db;
USE pharma_db;

-- 1. Drug details table
-- Records the details of every drug
CREATE TABLE drugs (
    drug_id INT PRIMARY KEY AUTO_INCREMENT,
    generic_name VARCHAR(100) NOT NULL,    -- generic name (e.g. Ibuprofen Sustained-Release Capsules)
    brand_name VARCHAR(100),               -- brand name (e.g. Fenbid)
    approval_number VARCHAR(50),           -- approval number (China drug approval no. H...)
    specifications VARCHAR(100),           -- specification (e.g. 0.3 g * 24 capsules/box)
    dosage_form VARCHAR(50),               -- dosage form (capsule/tablet/injection)
    manufacturer VARCHAR(100),             -- manufacturer
    therapeutic_area VARCHAR(50),          -- therapeutic area (e.g. analgesic/antipyretic, cardiovascular)
    description TEXT,                      -- drug details / indications
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Inventory table
-- Records drug stock levels, linked by drug_id
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    drug_id INT NOT NULL,

    batch_number VARCHAR(50) NOT NULL,     -- production batch number (a core field in pharma inventory)
    quantity_on_hand INT DEFAULT 0,        -- current stock on hand (boxes/bottles)
    warehouse_location VARCHAR(50),        -- warehouse location (e.g. Zone A - Rack 01)

    production_date DATE,                  -- production date
    expiry_date DATE,                      -- expiry date (used for alerts)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (drug_id) REFERENCES drugs(drug_id) ON DELETE CASCADE
);

-- 3. Sales records table
-- Records the sales of each drug, linked by drug_id
CREATE TABLE sales_records (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    drug_id INT NOT NULL,

    sale_date DATE NOT NULL,               -- sale date
    quantity_sold INT NOT NULL,            -- quantity sold
    unit_price DECIMAL(10, 2),             -- unit sale price
    total_amount DECIMAL(15, 2),           -- total sale amount

    customer_name VARCHAR(100),            -- customer name (e.g. XX First People's Hospital, XX Pharmacy)
    region VARCHAR(50),                    -- sales region (used for regional analysis)
    sales_rep VARCHAR(50),                 -- sales representative

    FOREIGN KEY (drug_id) REFERENCES drugs(drug_id) ON DELETE CASCADE
);

-- --- Insert mock data ---

-- 1. Insert 10 drugs (assume all are produced by our own company)
INSERT INTO drugs (generic_name, brand_name, approval_number, specifications, dosage_form, manufacturer, therapeutic_area, description)
VALUES
('Amoxicillin Capsules', 'Amoxin', 'H20051234', '0.25g*24 capsules', 'Capsule', 'Our Pharmaceutical Co.', 'Antibiotic', 'Used to treat upper respiratory tract infections, urogenital infections, and others caused by susceptible bacteria.'),
('Ibuprofen Sustained-Release Capsules', 'Fenbid', 'H10900089', '0.3g*20 capsules', 'Capsule', 'Our Pharmaceutical Co.', 'Analgesic/Antipyretic', 'Used to relieve mild to moderate pain such as headache, joint pain, migraine, toothache, muscle pain, neuralgia, and dysmenorrhea. Also used for fever caused by the common cold or influenza.'),
('Metformin Hydrochloride Tablets', 'Glucophage', 'H20023345', '0.5g*48 tablets', 'Tablet', 'Our Pharmaceutical Co.', 'Diabetes', 'First-line treatment for type 2 diabetes patients not adequately controlled by diet alone, especially those who are obese.'),
('Atorvastatin Calcium Tablets', 'Lipitor', 'H20055567', '20mg*7 tablets', 'Tablet', 'Our Pharmaceutical Co.', 'Cardiovascular', 'For patients with primary hypercholesterolemia, including familial hypercholesterolemia (heterozygous) or mixed hyperlipidemia.'),
('Oseltamivir Phosphate Capsules', 'Tamiflu', 'H20090123', '75mg*10 capsules', 'Capsule', 'Our Pharmaceutical Co.', 'Antiviral', 'For the treatment of influenza A and B in adults and children aged 1 year and older.'),
('Ceftriaxone Sodium for Injection', 'Rocephin', 'H10920012', '1.0g/vial', 'Injection', 'Our Pharmaceutical Co.', 'Antibiotic', 'For lower respiratory tract, urinary tract, and biliary infections caused by susceptible pathogens, as well as intra-abdominal infections, pelvic infections, skin and soft tissue infections, bone and joint infections, sepsis, meningitis, and more.'),
('Montmorillonite Powder', 'Smecta', 'H20000456', '3g*10 sachets', 'Powder', 'Our Pharmaceutical Co.', 'Digestive System', 'For acute and chronic diarrhea in adults and children.'),
('Nifedipine Controlled-Release Tablets', 'Adalat', 'H20100345', '30mg*30 tablets', 'Tablet', 'Our Pharmaceutical Co.', 'Hypertension', '1. Hypertension. 2. Coronary heart disease — chronic stable angina (exertional angina).'),
('Aspirin Enteric-Coated Tablets', 'Bayaspirin', 'J20130078', '100mg*30 tablets', 'Tablet', 'Our Pharmaceutical Co.', 'Cardiovascular', 'Reduces the risk of onset in patients with suspected acute myocardial infarction; prevents recurrence of myocardial infarction.'),
('Lianhua Qingwen Capsules', 'Lianhua Qingwen', 'Z20040063', '0.35g*24 capsules', 'Capsule', 'Our Pharmaceutical Co.', 'TCM / Cold & Flu', 'Clears heat-toxin and disperses lung heat. Used to treat influenza with heat-toxin attacking the lung, presenting as fever or high fever, chills, muscle aches, nasal congestion and runny nose, cough, headache, dry and sore throat.');

-- 2. Insert inventory data
-- Rule: 3 batches per drug (batch 2501, 2506, 2511)
-- Dates: all shifted to production in 2025, with expiry in 2027

INSERT INTO inventory (drug_id, batch_number, quantity_on_hand, warehouse_location, production_date, expiry_date)
VALUES
-- 1. Amoxicillin
(1, 'MY-250101-A', 5000, 'Beijing Warehouse 1 - Zone A', '2025-01-01', '2027-01-01'),
(1, 'MY-250615-B', 8000, 'Beijing Warehouse 2 - Zone B', '2025-06-15', '2027-06-14'),
(1, 'MY-251120-C', 12000, 'Tianjin Warehouse 1 - Zone A', '2025-11-20', '2027-11-19'),

-- 2. Ibuprofen
(2, 'MY-250101-A', 2000, 'Tianjin Warehouse 2 - Cold Storage', '2025-01-01', '2027-01-01'),
(2, 'MY-250615-B', 15000, 'Beijing Warehouse 1 - Zone C', '2025-06-15', '2027-06-14'),
(2, 'MY-251120-C', 30000, 'Tianjin Warehouse 1 - Zone A', '2025-11-20', '2027-11-19'),

-- 3. Metformin
(3, 'MY-250101-A', 3000, 'Beijing Warehouse 2 - Zone B', '2025-01-01', '2027-01-01'),
(3, 'MY-250615-B', 4500, 'Tianjin Warehouse 2 - Zone B', '2025-06-15', '2027-06-14'),
(3, 'MY-251120-C', 6000, 'Beijing Warehouse 1 - Zone A', '2025-11-20', '2027-11-19'),

-- 4. Atorvastatin
(4, 'MY-250101-A', 1000, 'Tianjin Warehouse 1 - High-Value Zone', '2025-01-01', '2027-01-01'),
(4, 'MY-250615-B', 2500, 'Beijing Warehouse 2 - High-Value Zone', '2025-06-15', '2027-06-14'),
(4, 'MY-251120-C', 4000, 'Tianjin Warehouse 2 - High-Value Zone', '2025-11-20', '2027-11-19'),

-- 5. Oseltamivir
(5, 'MY-250101-A', 500, 'Beijing Warehouse 1 - Emergency Drug Zone', '2025-01-01', '2027-01-01'),
(5, 'MY-250615-B', 5000, 'Tianjin Warehouse 1 - Emergency Drug Zone', '2025-06-15', '2027-06-14'),
(5, 'MY-251120-C', 20000, 'Beijing Warehouse 2 - Emergency Drug Zone', '2025-11-20', '2027-11-19'),

-- 6. Ceftriaxone
(6, 'MY-250101-A', 2000, 'Tianjin Warehouse 2 - Cool Storage', '2025-01-01', '2027-01-01'),
(6, 'MY-250615-B', 3500, 'Beijing Warehouse 2 - Cool Storage', '2025-06-15', '2027-06-14'),
(6, 'MY-251120-C', 5000, 'Tianjin Warehouse 1 - Cool Storage', '2025-11-20', '2027-11-19'),

-- 7. Montmorillonite Powder
(7, 'MY-250101-A', 4000, 'Beijing Warehouse 1 - General Drug Zone', '2025-01-01', '2027-01-01'),
(7, 'MY-250615-B', 8000, 'Tianjin Warehouse 2 - General Drug Zone', '2025-06-15', '2027-06-14'),
(7, 'MY-251120-C', 12000, 'Beijing Warehouse 2 - General Drug Zone', '2025-11-20', '2027-11-19'),

-- 8. Nifedipine
(8, 'MY-250101-A', 1500, 'Tianjin Warehouse 1 - Chronic Disease Zone', '2025-01-01', '2027-01-01'),
(8, 'MY-250615-B', 3000, 'Beijing Warehouse 1 - Chronic Disease Zone', '2025-06-15', '2027-06-14'),
(8, 'MY-251120-C', 5000, 'Tianjin Warehouse 2 - Chronic Disease Zone', '2025-11-20', '2027-11-19'),

-- 9. Aspirin
(9, 'MY-250101-A', 2000, 'Beijing Warehouse 2 - Ambient Zone', '2025-01-01', '2027-01-01'),
(9, 'MY-250615-B', 4500, 'Tianjin Warehouse 1 - Ambient Zone', '2025-06-15', '2027-06-14'),
(9, 'MY-251120-C', 7000, 'Beijing Warehouse 1 - Ambient Zone', '2025-11-20', '2027-11-19'),

-- 10. Lianhua Qingwen
(10, 'MY-250101-A', 10000, 'Tianjin Warehouse 2 - Epidemic Prevention Zone', '2025-01-01', '2027-01-01'),
(10, 'MY-250615-B', 50000, 'Beijing Warehouse 2 - Epidemic Prevention Zone', '2025-06-15', '2027-06-14'),
(10, 'MY-251120-C', 100000, 'Tianjin Warehouse 1 - Epidemic Prevention Zone', '2025-11-20', '2027-11-19');

-- 3. (Optional) Seed sales records for these 10 drugs — generated in the next step

INSERT INTO sales_records (drug_id, sale_date, quantity_sold, unit_price, total_amount, customer_name, region, sales_rep)
VALUES
-- 1. Amoxicillin
(1, '2025-02-15', 200, 25.00, 5000.00, 'Beijing Chaoyang Hospital', 'North China', 'Beijing Chaoyang Sales Dept.'),
(1, '2025-08-10', 500, 24.50, 12250.00, 'Tianjin Pharmacy', 'North China', 'Tianjin Nankai Sales Branch'),

-- 2. Ibuprofen
(2, '2025-01-20', 1000, 15.00, 15000.00, 'Neptunus Pharmacy Chain', 'East China', 'Hangzhou Binjiang Sales Dept.'),
(2, '2025-12-05', 5000, 15.00, 75000.00, 'Shanghai Huashan Hospital', 'East China', 'Shanghai Jing''an Sales HQ'),

-- 3. Metformin
(3, '2025-03-10', 300, 35.00, 10500.00, 'Guangzhou Sun Yat-sen Hospital', 'South China', 'Guangzhou Yuexiu Sales Dept.'),
(3, '2025-09-22', 400, 35.00, 14000.00, 'Shenzhen People''s Hospital', 'South China', 'Shenzhen Luohu Sales Branch'),

-- 4. Atorvastatin
(4, '2025-04-05', 100, 45.00, 4500.00, 'Chengdu West China Hospital', 'Southwest China', 'Chengdu Wuhou Sales Dept.'),
(4, '2025-10-18', 150, 45.00, 6750.00, 'Chongqing Pharmacy', 'Southwest China', 'Chongqing Yuzhong Sales Dept.'),

-- 5. Oseltamivir
(5, '2025-01-15', 2000, 100.00, 200000.00, 'Peking Union Medical College Hospital', 'North China', 'Beijing Dongdan Sales Dept.'),
(5, '2025-11-01', 5000, 100.00, 500000.00, 'Heilongjiang Provincial Hospital', 'Northeast China', 'Harbin Xiangfang Sales Dept.'),

-- 6. Ceftriaxone
(6, '2025-05-20', 500, 12.00, 6000.00, 'Wuhan Tongji Hospital', 'Central China', 'Wuhan Hankou Sales Dept.'),
(6, '2025-07-15', 600, 12.00, 7200.00, 'Changsha Xiangya Hospital', 'Central China', 'Changsha Kaifu Sales Dept.'),

-- 7. Montmorillonite Powder
(7, '2025-06-01', 1000, 18.00, 18000.00, 'Hangzhou First Hospital', 'East China', 'Hangzhou Shangcheng Sales Dept.'),
(7, '2025-08-25', 2000, 18.00, 36000.00, 'Nanjing Drum Tower Hospital', 'East China', 'Nanjing Gulou Sales Dept.'),

-- 8. Nifedipine
(8, '2025-02-28', 200, 30.00, 6000.00, 'Xi''an Xijing Hospital', 'Northwest China', 'Xi''an Xincheng Sales Dept.'),
(8, '2025-11-11', 500, 30.00, 15000.00, 'First Hospital of Lanzhou University', 'Northwest China', 'Lanzhou Chengguan Sales Dept.'),

-- 9. Aspirin
(9, '2025-03-15', 1000, 10.00, 10000.00, 'Jinan Central Hospital', 'East China', 'Jinan Lixia Sales Dept.'),
(9, '2025-09-09', 1200, 10.00, 12000.00, 'Qingdao Municipal Hospital', 'East China', 'Qingdao Shibei Sales Dept.'),

-- 10. Lianhua Qingwen
(10, '2025-01-10', 10000, 20.00, 200000.00, 'Shijiazhuang Yiling Pharmaceutical', 'North China', 'Shijiazhuang Hi-Tech Sales Dept.'),
(10, '2025-12-20', 50000, 20.00, 1000000.00, 'National Pharmacy Chain Central Warehouse', 'Nationwide', 'Corporate Key Accounts Dept.');
