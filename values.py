JOB_DATA_STRUCTURE = {
    "job_title": "",
    "job_description": "",
    "requirements": "",
    "company_name": "",
    "employment_type": "",
    "job_function": "",
    "industry": "",
    "job_id_or_ref_code": "",
    "posting_date": "",
    "job_location": "",
    "remote_status": "",
    "job_posting_source": "LinkedIn",
    "benefits": "",
    "required_experience": "",
    "required_education": "",
    "company_website": "",
    "company_profile": "",
    "company_size": "",
    "company_type": "",
    "company_founded_year": "",
    "company_social_media_links": [],
    "interview_location": "",
    "relocation_assistance": False,
    "application_link_or_email": "",
    "application_method_type": "",
    "response_time_claimed": "",
    "application_deadline": "",
    "recruiter_name_or_agency": "",
    "recruiter_contact_info": "",
    "hiring_manager_name": "",
    "salary_info_raw": "",
    "stock_options": False,
    "relocation_package": False,
    "number_of_positions": 0,
    "logo_present": False,
    "attachments": [],
    "posting_frequency": "",
    "posting_consistency": "",
    "external_reviews_available": False,
    "profile_photos_included": False,
    "expiration_date": ""
}

DEFAULT_JOB_DATA = {
    "job_title": "",
    "job_description": "",
    "requirements": "",
    "benefits": "",
    "employment_type": "",
    "required_experience": "",
    "required_education": "",
    "job_function": "",
    "industry": "",
    "job_id_or_ref_code": "",
    "posting_date": "",
    "expiration_date": "",
    "company_name": "",
    "company_profile": "",
    "company_website": "",
    "company_size": "",
    "company_type": "",
    "company_founded_year": "",
    "company_social_media_links": [],
    "job_location": "",
    "interview_location": "",
    "remote_status": "",
    "relocation_assistance": False,
    "application_link_or_email": "",
    "application_method_type": "",
    "response_time_claimed": "",
    "application_deadline": "",
    "recruiter_name_or_agency": "",
    "recruiter_contact_info": "",
    "hiring_manager_name": "",
    "salary_info_raw": "",
    "stock_options": False,
    "relocation_package": False,
    "job_posting_source": "LinkedIn",
    "number_of_positions": 0,
    "logo_present": False,
    "attachments": [],
    "posting_frequency": "",
    "posting_consistency": "",
    "external_reviews_available": False,
    "profile_photos_included": False,
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

SUSPICIOUS_PHRASES = [
    ('work from home', 'Work from home opportunities are commonly used in scams'),
    ('daily salary', 'Daily salary payments are unusual for legitimate jobs'),
    ('advance payment', 'Requests for advance payments are red flags'),
    ('immediate joining', 'Urgent hiring requests can indicate scams'),
    ('urgent hiring', 'Urgent hiring requests can indicate scams'),
    ('no experience needed', 'Legitimate jobs typically require some qualifications'),
    ('high salary for freshers', 'Exceptionally high salaries for freshers are suspicious'),
    ('earn money fast', 'Get-rich-quick phrases are common in scams'),
    ('no interview needed', 'Legitimate jobs always have some interview process'),
    ('part time job', 'Part-time job scams are common'),
    ('data entry job', 'Data entry jobs are frequently faked'),
    ('online job', 'Online job scams are prevalent'),
    ('easy money', 'Promises of easy money are red flags'),
    ('quick money', 'Promises of quick money are red flags'),
    ('no skills required', 'Legitimate jobs require some skills'),
    ('earn from home', 'Earn from home opportunities are often scams'),
    ('immediate start', 'Immediate start requests can indicate scams'),
    ('no background check', 'Legitimate employers conduct background checks'),
    ('direct hiring', 'Direct hiring without process is suspicious'),
    ('hiring now', 'Urgent hiring language can indicate scams'),
    ('urgent', 'Urgent language is often used to pressure candidates'),
    ('apply now', 'Immediate application pressure is suspicious'),
    ('limited seats', 'Artificial scarcity creates pressure'),
    ('offer expires', 'Time pressure tactics are common in scams'),
    ('act fast', 'Rush tactics are red flags'),
    ('last chance', 'Pressure tactics indicate potential scams'),
    ('hurry', 'Rush language is suspicious'),
    ('quick cash', 'Promises of quick money are red flags'),
    ('guaranteed income', 'Income guarantees are unrealistic'),
    ('life-changing opportunity', 'Overly dramatic promises are suspicious'),
    ('freelance opportunity', 'Vague freelance offers are often scams'),
    ('passive income', 'Passive income promises are often fake'),
    ('financial freedom', 'Unrealistic financial promises are red flags'),
    ('registration fee', 'Upfront fee requests are major red flags'),
    ('training fee', 'Training fee requests indicate scams'),
    ('investment required', 'Investment requirements are suspicious'),
    ('deposit needed', 'Deposit requests are red flags'),
    ('dream job', 'Overly appealing language is manipulative'),
    ('once-in-a-lifetime', 'Exclusive language creates false urgency'),
    ('exclusive offer', 'Exclusivity claims are often fake'),
    ('selected candidate', 'False selection claims are manipulative'),
    ('special opportunity', 'Special opportunity claims are often false'),
    ('work online', 'Vague online work descriptions are common in scams'),
    ('quick hiring', 'Fast hiring processes may indicate scams'),
    ('no resume needed', 'Legitimate jobs typically require resumes'),
    ('earn while learning', 'Promises of earning while training are suspicious'),
    ('no qualifications needed', 'Legitimate jobs typically require some qualifications'),
    ('international opportunity', 'Vague international offers may be scams'),
    ('work visa provided', 'Visa promises without proper process are suspicious'),
    ('instant job', 'No legitimate jobs are truly "instant"'),
    ('no experience necessary', 'Most jobs require some relevant experience')
]

URGENCY_KEYWORDS = [
    'urgent', 'immediate', 'apply now', 'limited seats', 'offer expires', 
    'act fast', 'last chance', 'hurry', 'immediate joining', 'urgent hiring',
    'immediate start', 'hiring now', 'offer valid', 'no interview needed',
    'quick hiring', 'limited time', 'apply immediately', 'fast hiring',
    'join immediately', 'urgent requirement', 'immediate opening'
]

HIGH_EARNING_PROMISES = [
    'easy money', 'quick cash', 'high salary', 'earn daily', 'guaranteed income',
    'life-changing opportunity', 'millionaires mentor', 'quick money', 'earn money fast',
    'high earnings', 'big profits', 'make money online', 'earn from home',
    'financial freedom', 'passive income', 'get rich quick', 'high commission',
    'unlimited earnings', 'earn thousands', 'make extra income', 'high paying',
    'lucrative opportunity', 'earn while you learn', 'money making'
]

VAGUE_TERMS = [
    'work from home', 'no experience needed', 'freelance opportunity', 'online job',
    'passive income', 'financial freedom', 'data entry job', 'online work',
    'flexible work', 'be your own boss', 'work online', 'earn from anywhere',
    'digital nomad', 'remote opportunity', 'work anytime', 'location independent',
    'internet job', 'home based', 'virtual job', 'online business'
]

PAYMENT_REQUESTS = [
    'advance payment', 'registration fee', 'training fee', 'investment required',
    'deposit needed', 'payment', 'fee', 'deposit', 'security deposit',
    'application fee', 'processing fee', 'admin fee', 'membership fee',
    'equipment cost', 'software purchase', 'starter kit', 'initial investment',
    'background check fee', 'verification fee', 'certification cost',
    'training materials', 'uniform cost', 'tool purchase'
]

FREE_EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'protonmail.com',
    'yandex.com', 'mail.com', 'rediffmail.com', '163.com', 'qq.com',
    'aol.com', 'zoho.com', 'gmx.com', 'icloud.com', 'live.com',
    'me.com', 'inbox.com', 'fastmail.com', 'hushmail.com', 'lycos.com'
]

SUSPICIOUS_TLDS = [
    '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.info', '.biz', '.online',
    '.site', '.club', '.click', '.download', '.stream', '.top', '.loan',
    '.win', '.review', '.date', '.guru', '.space', '.website', '.tech',
    '.store', '.digital', '.live', '.world', '.fun', '.bid', '.trade'
]

SUSPICIOUS_DOMAIN_KEYWORDS = [
    'job', 'career', 'recruit', 'hiring', 'work', 'earn', 'money', 'cash',
    'income', 'employment', 'opportunity', 'vacancy', 'position', 'apply',
    'offer', 'posting', 'opening', 'internship', 'placement', 'staffing'
]

SALARY_THRESHOLDS = {
    'daily_high': 5000,
    'monthly_high_fresher': 100000,
    'yearly_high_fresher': 3000000,
    'hourly_high': 2000
}

ROLE_SALARY_RANGES = {
    'data entry': {'min': 10000, 'max': 30000},
    'typing': {'min': 10000, 'max': 25000},
    'fresher software developer': {'min': 20000, 'max': 50000},
    'customer service': {'min': 15000, 'max': 35000},
    'content writer': {'min': 15000, 'max': 40000},
    'graphic designer': {'min': 18000, 'max': 45000},
    'digital marketing': {'min': 15000, 'max': 40000},
    'social media': {'min': 12000, 'max': 35000},
    'accountant': {'min': 25000, 'max': 60000},
    'hr executive': {'min': 20000, 'max': 50000},
    'business development': {'min': 25000, 'max': 70000},
    'sales executive': {'min': 15000, 'max': 40000},
    'teacher': {'min': 18000, 'max': 45000},
    'receptionist': {'min': 12000, 'max': 30000},
    'office assistant': {'min': 12000, 'max': 30000}
}

GRAMMAR_INDICATORS = {
    'excessive_caps_threshold': 0.2,
    'excessive_exclamation_threshold': 5,
    'double_exclamation_threshold': 0,
    'spelling_error_threshold': 0.1,
    'sentence_length_variance': 0.8
}