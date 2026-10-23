"""All portfolio content, taken from Jessie J.'s resume (typos corrected, nothing invented).

Private details on the resume (home address, date of birth, gender) are deliberately left out.
"""

PERSON = {
    "name": "Jessie J.",
    "role": "Physiotherapist",
    "focus": "Sports & orthopaedic rehabilitation",
    "city": "Chennai, India",
    "email": "jessieraj57@gmail.com",
    "phone_display": "+91 79044 27531",
    "phone_link": "+917904427531",
    "whatsapp": "https://wa.me/917904427531",
}

NAV = [
    ("about", "About"),
    ("approach", "Approach"),
    ("expertise", "Expertise"),
    ("experience", "Experience"),
    ("research", "Research"),
    ("education", "Education"),
    ("contact", "Contact"),
]

FACTS = [
    ("Degree", "BPT · SIMATS"),
    ("In practice", "Since 2022"),
    ("Languages", "EN · TA · ML"),
]

MARQUEE = [
    "Sports injury rehab", "Post-operative rehab", "Manual therapy", "Neuro rehabilitation",
    "Return to play", "Muscle energy technique", "Geriatric care", "Trigger point release",
    "Paediatric physiotherapy", "Cupping therapy", "Fall prevention", "Electrotherapy",
]

# The care pathway. Angles mark positions on the goniometer dial (0 to 180 degrees).
STAGES = [
    {
        "key": "assess", "angle": 0, "title": "Assess",
        "text": "Every plan starts with measurement: muscle strength, range of motion, balance, gait "
                "and functional mobility, plus biomechanical and movement analysis to find what is "
                "holding the person back.",
    },
    {
        "key": "plan", "angle": 45, "title": "Plan",
        "text": "An individual programme built around the person's functional goals, their home "
                "environment and their medical condition, so the work fits the life they need to get back to.",
    },
    {
        "key": "treat", "angle": 90, "title": "Treat",
        "text": "Therapeutic exercise, manual therapy and electrotherapy, with muscle energy technique, "
                "trigger point release and cupping where they help with pain, mobility and strength.",
    },
    {
        "key": "educate", "angle": 135, "title": "Educate",
        "text": "Home exercise programmes, posture correction, ergonomics, fall prevention and safe "
                "mobility, taught to patients and the family members and caregivers who support them.",
    },
    {
        "key": "return", "angle": 180, "title": "Return",
        "text": "Regular reassessment and adjusted plans until the person is back to daily activity, "
                "or back to sport through return-to-play protocols and injury prevention.",
    },
]

EXPERTISE = [
    {
        "key": "sports", "title": "Sports injuries",
        "caption": "Knees and ankles: common sites of sports injury.",
        "text": "Assessment and rehabilitation of sports injuries, from the first session through "
                "return-to-play protocols and strategies that lower the risk of the next injury.",
        "items": ["Sports injury management", "Return to play", "Injury prevention", "Movement analysis"],
    },
    {
        "key": "ortho", "title": "Orthopaedic and post-operative",
        "caption": "Shoulder, spine, hip and knee, including recovery after joint replacement.",
        "text": "Recovery after joint replacement, fractures and ligament injuries, and care for "
                "acute and chronic musculoskeletal conditions.",
        "items": ["Post-fracture recovery", "Joint mobility restoration", "Muscle strengthening", "Pain management"],
    },
    {
        "key": "neuro", "title": "Neurological rehabilitation",
        "caption": "Brain and spine, with balance and gait as the measures that matter.",
        "text": "Programmes for stroke and other neurological conditions built on gait re-education, "
                "balance and coordination training, and motor control work.",
        "items": ["Gait re-education", "Balance training", "Neuromuscular re-education", "Functional mobility"],
    },
    {
        "key": "lifespan", "title": "Children and older adults",
        "caption": "Hips, ankles and standing balance: the focus of fall prevention.",
        "text": "Paediatric work on motor development, balance and coordination, and geriatric rehab "
                "focused on strength, gait and fall prevention at home and in residential care.",
        "items": ["Paediatric physiotherapy", "Geriatric rehabilitation", "Fall prevention", "Home-based care"],
    },
    {
        "key": "hands", "title": "Hands-on techniques",
        "caption": "Soft-tissue and joint work along the shoulders and spine.",
        "text": "The manual and modality toolkit used across every programme, chosen for what each "
                "person's assessment shows.",
        "items": ["Manual therapy", "Muscle energy technique", "Trigger point release", "Cupping therapy",
                  "Therapeutic exercise", "Electrotherapy"],
    },
]

PRACTICE = [
    {
        "dates": "Feb 2025 – Present",
        "role": "Clinical Physiotherapist",
        "org": "Best Move Physio and Rehab Centre",
        "place": "Chennai",
        "summary": "Rehabilitation with a primary focus on orthopaedic and sports injury management, "
                   "alongside paediatric physiotherapy. I also mentor junior physiotherapists and interns.",
        "bullets": [
            "Delivered comprehensive rehabilitation services with a primary focus on orthopaedic and sports injury management, alongside paediatric physiotherapy care.",
            "Evaluated and treated acute and chronic musculoskeletal conditions, improving functional outcomes and quality of life.",
            "Provided post-operative orthopaedic rehabilitation focused on pain management, range of motion restoration, muscle strengthening and functional recovery.",
            "Implemented neurological rehabilitation programmes with gait re-education, balance training, neuromuscular re-education and functional mobility exercises.",
            "Conducted biomechanical assessments and movement analysis to identify impairments, improve movement efficiency and minimise injury risk.",
            "Integrated therapeutic exercise, manual therapy and electrotherapy to improve mobility, strength, coordination and functional independence.",
            "Monitored progress through regular reassessments and modified treatment plans to reach the best clinical outcomes.",
            "Collaborated with patients, caregivers and multidisciplinary healthcare professionals to deliver individualised, patient-centred rehabilitation.",
            "Mentored junior physiotherapists and interns in orthopaedic and neurological assessment, treatment planning, clinical reasoning and evidence-based techniques.",
            "Facilitated clinical learning through case discussions, practical demonstrations and supervised hands-on training.",
        ],
    },
    {
        "dates": "Present",
        "role": "Independent Physiotherapist",
        "org": "Home-based practice",
        "place": "Freelance",
        "summary": "Assessment and rehabilitation in patients' homes and residential elderly care "
                   "settings, with a focus on balance, gait, fall prevention and independence.",
        "bullets": [
            "Provided physiotherapy in patients' homes and residential elderly care settings, with individualised assessment and rehabilitation programmes.",
            "Managed orthopaedic, neurological, post-operative and age-related musculoskeletal conditions, focusing on pain management, mobility and functional independence.",
            "Delivered geriatric rehabilitation to improve balance, strength, gait, fall prevention and overall quality of life.",
            "Developed personalised treatment plans tailored to each patient's functional goals, home environment and medical condition.",
            "Educated patients, family members and caregivers on therapeutic exercise, mobility strategies and long-term self-management.",
            "Monitored progress through regular reassessments and adapted interventions to improve recovery and functional outcomes.",
            "Promoted safe mobility and independence through evidence-based rehabilitation and patient-centred care.",
        ],
    },
    {
        "dates": "Aug 2022 – Dec 2024",
        "role": "Clinical Physiotherapist",
        "org": "New Life Multi Speciality Clinic",
        "place": "Chennai",
        "summary": "Assessment, treatment and rehabilitation for sports injuries, musculoskeletal "
                   "disorders, neurological conditions and paediatric developmental impairments.",
        "bullets": [
            "Managed assessment, treatment and rehabilitation of patients with sports injuries, musculoskeletal disorders, neurological conditions and paediatric developmental impairments.",
            "Conducted comprehensive orthopaedic and neurological assessments, including muscle strength, range of motion, balance, gait and functional mobility.",
            "Designed and implemented individualised rehabilitation programmes for musculoskeletal injuries, post-operative conditions, stroke and other neurological disorders.",
            "Applied therapeutic exercise, manual therapy and electrotherapy to improve pain, mobility, strength and functional independence.",
            "Provided neurorehabilitation through gait re-education, balance and coordination training, motor control exercises and functional mobility work.",
            "Monitored progress through regular reassessments and modified treatment plans to support recovery, prevent complications and promote independence in daily activities.",
            "Implemented evidence-based strategies for post-fracture recovery, joint mobility restoration, muscle strengthening and post-surgical rehabilitation.",
            "Educated patients and caregivers on home exercise programmes, posture correction, fall prevention and safe mobility techniques.",
        ],
    },
]

INTERNSHIPS = [
    {
        "dates": "Jan 2026 – Mar 2026",
        "role": "Physiotherapy Intern",
        "org": "Vijaya Hospitals",
        "place": "Chennai",
        "summary": "Supervised assessments across orthopaedic, sports, paediatric, obstetrics and "
                   "gynaecology, geriatric and neurological rehabilitation.",
        "bullets": [
            "Assisted in the assessment of patients across orthopaedic, sports, paediatric, obstetrics and gynaecology, geriatric and neurological rehabilitation departments under the supervision of senior physiotherapists.",
            "Gained hands-on experience in post-operative orthopaedic rehabilitation, including joint replacement, fracture management and ligament injury recovery.",
            "Assisted in sports rehabilitation programmes involving therapeutic exercise, injury prevention strategies and return-to-play protocols.",
            "Observed and assisted in paediatric physiotherapy focused on motor development, balance, coordination and functional mobility.",
        ],
    },
    {
        "dates": "Sep 2025 – Dec 2025",
        "role": "Physiotherapy Intern",
        "org": "Saveetha Medical College and Hospitals",
        "place": "Chennai",
        "summary": "Clinical rotations across ten departments, from orthopaedics and sports "
                   "rehabilitation to the ICU and community-based rehabilitation.",
        "bullets": [
            "Completed clinical rotations across Orthopaedics, Sports Rehabilitation, Neurology, Paediatrics, Cardiorespiratory, General Medicine, General Surgery, ICU, Community-Based Rehabilitation and Geriatric Physiotherapy.",
            "Participated in the assessment and treatment of patients with neurological conditions, focusing on balance training, gait re-education, coordination and functional mobility.",
            "Took part in interdisciplinary rounds, case presentations, clinical discussions and treatment planning sessions.",
            "Educated patients and caregivers on home exercise programmes, lifestyle modifications, ergonomics and injury prevention.",
            "Maintained accurate patient documentation and monitored treatment outcomes throughout rehabilitation.",
        ],
    },
]

ROTATION_SITES = ["Saveetha Medical College and Hospitals", "Vijaya Hospitals", "Chennai National Hospital"]

RESEARCH = [
    {
        "key": "knee",
        "title": "Weight-bearing exercise for balance and proprioception in knee osteoarthritis",
        "lead": "A study of the effectiveness of static and dynamic weight-bearing exercises on balance "
                "and proprioception in people with osteoarthritis of the knee.",
        "rows": [
            ("Population", "Individuals with knee osteoarthritis"),
            ("Intervention", "Static and dynamic weight-bearing exercises"),
            ("Outcomes", "Balance and proprioception"),
        ],
    },
    {
        "key": "parkinsons",
        "title": "Facial massage and oral motor exercises for sialorrhea in Parkinson's disease",
        "lead": "A study of the effectiveness of facial massage and oral motor exercises on sialorrhea, "
                "or excessive drooling, in people living with Parkinson's disease.",
        "rows": [
            ("Population", "Individuals with Parkinson's disease"),
            ("Intervention", "Facial massage and oral motor exercises"),
            ("Outcome", "Sialorrhea (excessive drooling)"),
        ],
    },
]

EDUCATION = [
    ("2021 – 2026", "Bachelor of Physiotherapy (BPT)", "Saveetha College of Physiotherapy, SIMATS", "Chennai, Tamil Nadu"),
    ("2019 – 2021", "Higher Secondary Certificate", "Maria Matriculation School", "Chennai, Tamil Nadu"),
    ("2018 – 2019", "Secondary School Leaving Certificate", "St. Kevin's AIHSS", "Chennai, Tamil Nadu"),
]

CERTIFICATIONS = [
    ("Cupping therapy", "A suction-based technique for soft-tissue tension."),
    ("Trigger point release", "Manual release of tight, tender points within a muscle."),
    ("Muscle energy technique", "The patient's own muscle contractions used to restore mobility."),
]

LANGUAGES = [
    ("English", "Professional proficiency"),
    ("Tamil", "Native"),
    ("Malayalam", "Basic, improving"),
]
