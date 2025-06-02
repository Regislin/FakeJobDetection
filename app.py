from flask import Flask, request, render_template, redirect, url_for, jsonify
import joblib
import os
import pandas as pd
import random
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import csv
import logging
import time
from nltk.tokenize import sent_tokenize
import nltk
from urllib.parse import urlparse
import dns.resolver
import whois
from values import *

# Import enhanced verification functions (modified to exclude removed functions)
from verify import enhanced_scam_detection, detect_scam_job

app = Flask(__name__)

"""nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('vader_lexicon')"""

model = joblib.load('job_model_catboost.pkl')
vectorizer = joblib.load('vectorizer_catboost.pkl')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text(text):
    if not text:
        return text
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_linkedin_job(url):
    job_id_match = re.search(r"/jobs/view/(\d+)/", url)
    job_id = job_id_match.group(1) if job_id_match else ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                break
            logging.warning(f"Attempt {attempt + 1} failed with status code: {response.status_code}")
            time.sleep(2 ** attempt)
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            if attempt == max_retries - 1:
                return {"error": f"Failed to fetch job page after {max_retries} attempts."}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    job_data = JOB_DATA_STRUCTURE.copy()
    job_data["job_id_or_ref_code"] = job_id
    
    try:
        title_elem = soup.find("h1", class_="top-card-layout__title")
        job_data["job_title"] = clean_text(title_elem.text) if title_elem else ""
    except Exception as e:
        logging.warning(f"Failed to extract job title: {e}")
    
    try:
        company_elem = soup.find("a", class_="topcard__org-name-link")
        job_data["company_name"] = clean_text(company_elem.text) if company_elem else ""
    except Exception as e:
        logging.warning(f"Failed to extract company name: {e}")
    
    description_section = soup.find("div", class_="show-more-less-html__markup")
    if description_section:
        full_text = description_section.get_text(separator=" ", strip=True)
        full_text = clean_text(full_text)
        
        sections = re.split(r'(?=[A-Z][a-z]+:)', full_text)
        if len(sections) == 1:
            sections = re.split(r'(?=\b(?:Requirements|Qualifications|Skills|What You\'ll Need|You Have|About the Role|Job Description|Responsibilities)\b)', 
                               full_text, flags=re.IGNORECASE)
        
        description_parts = []
        requirements_parts = []
        benefits_parts = []
        
        for section in sections:
            section = clean_text(section)
            if not section:
                continue
                
            if re.search(r'^(Requirements|Qualifications|Skills|What You\'ll Need|You Have|Must Have)', 
                        section, re.IGNORECASE):
                requirements_parts.append(section)
            elif re.search(r'^(Benefits|Perks|What We Offer)', section, re.IGNORECASE):
                benefits_parts.append(section)
            elif re.search(r'^(About the Role|Job Description|Responsibilities)', 
                          section, re.IGNORECASE):
                description_parts.append(section)
            else:
                if not requirements_parts and re.search(r'\b(experience|knowledge|skills|ability|degree|qualifications?)\b', 
                                                      section, re.IGNORECASE):
                    requirements_parts.append(section)
                else:
                    description_parts.append(section)
        
        if description_parts:
            job_data["job_description"] = ' '.join(description_parts)
        else:
            job_data["job_description"] = full_text
        
        if requirements_parts:
            job_data["requirements"] = ' '.join(requirements_parts)
        else:
            req_sentences = []
            sentences = sent_tokenize(full_text)
            for sentence in sentences:
                if re.search(r'\b(experience|knowledge|skills|ability|degree|qualifications?|proficient|familiar|understanding)\b', 
                            sentence, re.IGNORECASE):
                    req_sentences.append(sentence)
            if req_sentences:
                job_data["requirements"] = ' '.join(req_sentences)
        
        if benefits_parts:
            job_data["benefits"] = ' '.join(benefits_parts)
    
    try:
        criteria_section = soup.find("ul", class_="description__job-criteria-list")
        if criteria_section:
            for item in criteria_section.find_all("li"):
                header = clean_text(item.find("h3").text) if item.find("h3") else ""
                value = clean_text(item.find("span").text) if item.find("span") else ""
                if "employment type" in header.lower():
                    job_data["employment_type"] = value
                elif "job function" in header.lower():
                    job_data["job_function"] = value
                elif "industries" in header.lower():
                    job_data["industry"] = value
                elif "seniority level" in header.lower():
                    job_data["required_experience"] = value
    except Exception as e:
        logging.warning(f"Failed to extract criteria: {e}")
    
    try:
        posting_date = soup.find("span", class_="posted-time-ago__text")
        job_data["posting_date"] = clean_text(posting_date.text) if posting_date else ""
    except Exception as e:
        logging.warning(f"Failed to extract posting date: {e}")
    
    try:
        location = soup.find("span", class_="topcard__flavor--bullet")
        job_data["job_location"] = clean_text(location.text) if location else ""
    except Exception as e:
        logging.warning(f"Failed to extract location: {e}")
    
    try:
        remote_status = soup.find("span", class_="workplace-type")
        job_data["remote_status"] = clean_text(remote_status.text.capitalize()) if remote_status else ""
    except Exception as e:
        logging.warning(f"Failed to extract remote status: {e}")
    
    try:
        company_link = soup.find("a", class_="topcard__org-name-link")["href"]
        if company_link:
            job_data["company_social_media_links"].append(company_link)
            if "linkedin.com" in company_link:
                job_data["company_website"] = company_link
    except Exception as e:
        logging.warning(f"Failed to extract company links: {e}")
    
    try:
        if description_section:
            salary_matches = re.findall(r"\$[\d,]+(?:\.\d{2})?(?:\s*-\s*\$[\d,]+(?:\.\d{2})?)?", description_section.text)
            if salary_matches:
                job_data["salary_info_raw"] = ", ".join(salary_matches)
    except Exception as e:
        logging.warning(f"Failed to extract salary info: {e}")
    
    for key in job_data:
        if isinstance(job_data[key], str):
            job_data[key] = clean_text(job_data[key])
    
    return job_data

def check_suspicious_phrases(text):
    suspicious_found = []
    reasons = []
    text_lower = text.lower()
    
    for phrase, reason in SUSPICIOUS_PHRASES:
        if phrase in text_lower:
            suspicious_found.append(phrase)
            reasons.append(reason)
    
    return suspicious_found, reasons

def check_salary_anomalies(salary_info, required_exp):
    issues = []
    reasons = []
    
    if not salary_info:
        return issues, reasons
    
    salary_lower = salary_info.lower()
    salary_numbers = re.findall(r'[\d,]+\.?\d*', salary_info)
    
    if salary_numbers:
        salaries = [float(num.replace(',', '')) for num in salary_numbers]
        exp_lower = required_exp.lower() if required_exp else ""
        
        is_fresher = any(term in exp_lower for term in ['entry', 'fresher', '0', 'no experience'])
        
        for salary in salaries:
            if 'day' in salary_lower and salary > SALARY_THRESHOLDS['daily_high']:
                issues.append('unrealistic_daily_salary')
                reasons.append(f"Unrealistically high daily salary ({salary} INR)")
                break
            elif ('month' in salary_lower or 'per month' in salary_lower) and is_fresher and salary > SALARY_THRESHOLDS['monthly_high_fresher']:
                issues.append('unrealistic_monthly_salary')
                reasons.append(f"Unrealistically high monthly salary ({salary} INR) for entry-level")
                break
            elif ('year' in salary_lower or 'annual' in salary_lower) and is_fresher and salary > SALARY_THRESHOLDS['yearly_high_fresher']:
                issues.append('unrealistic_annual_salary')
                reasons.append(f"Unrealistically high annual salary ({salary} INR) for entry-level")
                break
            elif 'hour' in salary_lower and salary > SALARY_THRESHOLDS['hourly_high']:
                issues.append('unrealistic_hourly_salary')
                reasons.append(f"Unrealistically high hourly rate ({salary} INR)")
                break
    
    return issues, reasons

def check_email_domains(email_or_website):
    issues = []
    reasons = []
    
    if not email_or_website:
        return issues, reasons
    
    email_matches = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', email_or_website)
    url_matches = re.findall(r'https?://[\w\.-]+\.\w+', email_or_website)
    
    all_domains = []
    
    for email in email_matches:
        domain = email.split('@')[1].lower()
        all_domains.append(domain)
        
        if any(free_domain in domain for free_domain in FREE_EMAIL_DOMAINS):
            issues.append('free_email_domain')
            reasons.append(f'Use of free email domain: {domain}')
    
    for url in url_matches:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        all_domains.append(domain)
    
    for domain in all_domains:
        if any(tld in domain for tld in SUSPICIOUS_TLDS):
            issues.append('suspicious_tld')
            reasons.append(f'Suspicious domain extension: {domain}')
        
        if any(keyword in domain for keyword in SUSPICIOUS_DOMAIN_KEYWORDS):
            issues.append('suspicious_domain_keywords')
            reasons.append(f'Suspicious domain with job-related keywords: {domain}')
    
    return issues, reasons

def check_urgency_indicators(text):
    issues = []
    reasons = []
    
    text_lower = text.lower()
    urgency_count = sum(1 for keyword in URGENCY_KEYWORDS if keyword in text_lower)
    
    if urgency_count >= 3:
        issues.append('high_urgency')
        reasons.append('Multiple urgency indicators suggest pressure tactics')
    elif urgency_count >= 1:
        issues.append('urgency_present')
        reasons.append('Urgency language may indicate rushed hiring process')
    
    return issues, reasons

def check_vague_descriptions(form_data):
    issues = []
    reasons = []
    
    job_title = form_data.get('job_title', '').lower()
    job_desc = form_data.get('job_description', '').lower()
    
    vague_count = sum(1 for term in VAGUE_TERMS if term in job_title or term in job_desc)
    
    if vague_count >= 2:
        issues.append('highly_vague')
        reasons.append('Job description contains multiple vague terms')
    elif vague_count >= 1:
        issues.append('somewhat_vague')
        reasons.append('Job description contains vague terminology')
    
    if not form_data.get('company_name') or len(form_data.get('company_name', '').strip()) < 3:
        issues.append('missing_company_info')
        reasons.append('Missing or insufficient company information')
    
    return issues, reasons

def advanced_scam_detection(form_data):
    all_issues = []
    all_reasons = []
    
    text_fields = [
        form_data.get('job_title', ''),
        form_data.get('job_description', ''),
        form_data.get('requirements', ''),
        form_data.get('benefits', '')
    ]
    combined_text = ' '.join(text_fields)
    
    phrase_issues, phrase_reasons = check_suspicious_phrases(combined_text)
    all_issues.extend(phrase_issues)
    all_reasons.extend(phrase_reasons)
    
    salary_issues, salary_reasons = check_salary_anomalies(
        form_data.get('salary_info_raw', ''),
        form_data.get('required_experience', '')
    )
    all_issues.extend(salary_issues)
    all_reasons.extend(salary_reasons)
    
    email_or_website = form_data.get('application_link_or_email', '') or form_data.get('company_website', '')
    email_issues, email_reasons = check_email_domains(email_or_website)
    all_issues.extend(email_issues)
    all_reasons.extend(email_reasons)
    
    urgency_issues, urgency_reasons = check_urgency_indicators(combined_text)
    all_issues.extend(urgency_issues)
    all_reasons.extend(urgency_reasons)
    
    vague_issues, vague_reasons = check_vague_descriptions(form_data)
    all_issues.extend(vague_issues)
    all_reasons.extend(vague_reasons)
    
    if form_data.get('remote_status', '').lower() == 'remote' and not form_data.get('job_location'):
        all_issues.append('remote_no_location')
        all_reasons.append('Remote job without company location specified')
    
    response_time = form_data.get('response_time_claimed', '').lower()
    if any(term in response_time for term in ['immediate', 'within 24 hours', 'urgent']):
        all_issues.append('unrealistic_response_time')
        all_reasons.append('Unrealistically quick response time promised')
    
    return list(set(all_issues)), all_reasons

def save_user_input_to_csv(form_data, prediction_result):
    csv_filename = 'userinputs.csv'
    
    fieldnames = [
        'job_title', 'job_description', 'requirements', 'benefits', 'employment_type',
        'required_experience', 'required_education', 'job_function', 'industry',
        'job_id_or_ref_code', 'posting_date', 'expiration_date', 'company_name',
        'company_profile', 'company_website', 'company_size', 'company_type',
        'company_founded_year', 'company_social_media_links__-', 'job_location',
        'interview_location', 'remote_status', 'relocation_assistance',
        'application_link_or_email', 'application_method_type', 'response_time_claimed',
        'application_deadline', 'recruiter_name_or_agency', 'recruiter_contact_info',
        'hiring_manager_name', 'salary_info_raw', 'stock_options', 'relocation_package',
        'job_posting_source', 'number_of_positions', 'logo_present', 'attachments__-',
        'posting_frequency', 'posting_consistency', 'external_reviews_available',
        'profile_photos_included', 'is_real'
    ]
    
    file_exists = os.path.isfile(csv_filename)
    
    row_data = []
    for field in fieldnames[:-1]:
        if field == 'company_social_media_links__-':
            social_links = form_data.get('company_social_media_links', [])
            if isinstance(social_links, list):
                value = ', '.join(str(link) for link in social_links) if social_links else ''
            else:
                value = str(social_links) if social_links else ''
        elif field == 'attachments__-':
            attachments = form_data.get('attachments', [])
            if isinstance(attachments, list):
                value = ', '.join(str(att) for att in attachments) if attachments else ''
            else:
                value = str(attachments) if attachments else ''
        else:
            value = str(form_data.get(field, '')) if form_data.get(field) else ''
        
        value = value.replace('\n', ' ').replace('\r', ' ').replace(',', ';') if value else ''
        row_data.append(value)
    
    row_data.append(str(1 if prediction_result == "Real Job" else 0))
    
    with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if not file_exists:
            writer.writerow(fieldnames)
        
        writer.writerow(row_data)
        
def analyze_suspicious_features(form_data):
    suspicious_features = []
    basic_reasons = []
    
    salary_info = form_data.get('salary_info_raw', '').lower()
    if salary_info:
        salary_numbers = re.findall(r'[\d,]+\.?\d*', salary_info)
        if salary_numbers:
            salaries = [float(num.replace(',', '')) for num in salary_numbers]
            
            required_exp = form_data.get('required_experience', '').lower()
            if 'entry' in required_exp or 'fresher' in required_exp or '0' in required_exp:
                for salary in salaries:
                    if 'day' in salary_info and salary > 5000:
                        suspicious_features.append('salary')
                        basic_reasons.append(f"Unrealistically high daily salary ({salary} INR) for entry-level position")
                        break
                    elif ('month' in salary_info or 'per month' in salary_info) and salary > 100000:
                        suspicious_features.append('salary')
                        basic_reasons.append(f"Unrealistically high monthly salary ({salary} INR) for entry-level position")
                        break
                    elif ('year' in salary_info or 'annual' in salary_info) and salary > 3000000:
                        suspicious_features.append('salary')
                        basic_reasons.append(f"Unrealistically high annual salary ({salary} INR) for entry-level position")
                        break
    
    text_fields = [
        form_data.get('job_description', ''),
        form_data.get('requirements', ''),
        form_data.get('benefits', '')
    ]
    combined_text = ' '.join(text_fields).lower()
    
    basic_suspicious_phrases = [
        ('work from home', 'Work from home opportunities are commonly used in scams'),
        ('daily salary', 'Daily salary payments are unusual for legitimate jobs'),
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
        ('hiring now', 'Urgent hiring language can indicate scams')
    ]
    
    for phrase, reason in basic_suspicious_phrases:
        if phrase in combined_text:
            if 'suspicious phrases' not in suspicious_features:
                suspicious_features.append('suspicious phrases')
                basic_reasons.append(reason)
    
    # Removed excessive capitalization and exclamation checks (grammar-related)
    
    email_or_website = form_data.get('application_link_or_email', '') or form_data.get('company_website', '')
    if email_or_website:
        if '@gmail.' in email_or_website or '@yahoo.' in email_or_website or '@hotmail.' in email_or_website:
            suspicious_features.append('unprofessional contact')
            basic_reasons.append('Use of free email domains (Gmail, Yahoo) instead of company domain')
        
        basic_suspicious_domains = [
            '.ru', '.tk', '.ml', '.ga', '.cf', '.gq',
            'job', 'career', 'recruit', 'hiring', 'work'
        ]
        
        parsed_url = urlparse(email_or_website)
        domain = parsed_url.netloc or parsed_url.path.split('@')[-1].split('/')[0]
        
        for d in basic_suspicious_domains:
            if d in domain:
                suspicious_features.append('suspicious domain')
                basic_reasons.append(f'Suspicious domain detected: {domain}')
                break
    
    if not form_data.get('company_name') or not form_data.get('company_website'):
        suspicious_features.append('missing company info')
        basic_reasons.append('Missing or incomplete company information')
    
    if form_data.get('remote_status', '').lower() == 'remote' and not form_data.get('job_location'):
        suspicious_features.append('remote job with no location')
        basic_reasons.append('Remote job postings should still specify company location')
    
    response_time = form_data.get('response_time_claimed', '').lower()
    if 'immediate' in response_time or 'within 24 hours' in response_time or 'urgent' in response_time:
        suspicious_features.append('urgent response time')
        basic_reasons.append('Unrealistically quick response times are common in scams')
    
    # Removed payment request detection
    
    return suspicious_features, basic_reasons

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    form_data = {}
    for field in request.form:
        form_data[field] = request.form[field]
    
    job_title = form_data.get('job_title', '')
    job_desc = form_data.get('job_description', '')
    requirements = form_data.get('requirements', '')
    benefits = form_data.get('benefits', '')
    
    combined_text = f"{job_title} {job_desc} {requirements} {benefits}"
    text_vec = vectorizer.transform([combined_text])
    prediction = model.predict(text_vec)
    model_result = "Real Job" if prediction[0] == 1 else "Fake Job"
    
    final_result = model_result
    save_user_input_to_csv(form_data, final_result)
    all_suspicious_features = []
    all_reasons = []
    enhanced_verification_used = False
    critical_issues_count = 0
    
    if model_result == "Real Job":
        try:
            verification_result = enhanced_scam_detection(form_data)
            enhanced_verification_used = True
            critical_issues_count = verification_result.get('critical_issues', 0)
            
            if (verification_result['is_scam'] or 
                critical_issues_count >= 2 or 
                verification_result['total_issues'] >= 5):
                
                final_result = "Fake Job"
                all_suspicious_features = verification_result['issues']
                all_reasons = verification_result['reasons']
                logging.info(f"CatBoost prediction OVERRIDDEN: {job_title} - "
                             f"Critical issues: {critical_issues_count}, "
                             f"Total issues: {verification_result['total_issues']}")
            else:
                all_suspicious_features = verification_result['issues']
                all_reasons = verification_result['reasons']
        except Exception as e:
            logging.error(f"Enhanced verification failed: {e}")
            basic_suspicious_features, basic_reasons = analyze_suspicious_features(form_data)
            all_suspicious_features = basic_suspicious_features
            all_reasons = basic_reasons
    else:
        basic_suspicious_features, basic_reasons = analyze_suspicious_features(form_data)
        advanced_issues, advanced_reasons = advanced_scam_detection(form_data)
        all_suspicious_features = list(set(basic_suspicious_features + advanced_issues))
        all_reasons = basic_reasons + advanced_reasons
    
    display_suspicious_features = all_suspicious_features.copy()
    display_reasons = all_reasons.copy()
    
    if final_result == "Real Job" and len(all_suspicious_features) > 2:
        num_to_show = random.randint(1, 2)
        
        if len(all_suspicious_features) == len(all_reasons):
            paired_items = list(zip(all_suspicious_features, all_reasons))
            selected_pairs = random.sample(paired_items, min(num_to_show, len(paired_items)))
            display_suspicious_features, display_reasons = zip(*selected_pairs) if selected_pairs else ([], [])
            display_suspicious_features = list(display_suspicious_features)
            display_reasons = list(display_reasons)
        else:
            display_suspicious_features = random.sample(all_suspicious_features, min(num_to_show, len(all_suspicious_features)))
            display_reasons = random.sample(all_reasons, min(num_to_show, len(all_reasons)))
        
        logging.info(f"Limited red flags for Real Job '{job_title}': "
                     f"Total found: {len(all_suspicious_features)}, "
                     f"Showing: {len(display_suspicious_features)}")
    
    if all_suspicious_features:
        if final_result == "Fake Job":
            if enhanced_verification_used and critical_issues_count >= 2:
                score = max(5, 95 - (critical_issues_count * 15) - (len(all_suspicious_features) * 8))
            else:
                score = max(10, 90 - (len(all_suspicious_features) * 12))
        else:
            score = max(50, 80 - (len(all_suspicious_features) * 8))
    else:
        score = random.randint(60, 89) if final_result == "Real Job" else random.randint(70, 95)
    
    if enhanced_verification_used:
        logging.info(f"Enhanced verification for '{job_title}': "
                     f"Model={model_result}, Final={final_result}, "
                     f"Critical={critical_issues_count}, Total={len(all_suspicious_features)}, "
                     f"Score={score}")
    
    verification_details = {
        'model_prediction': model_result,
        'final_prediction': final_result,
        'override_applied': model_result != final_result,
        'critical_issues_count': critical_issues_count,
        'total_issues_count': len(all_suspicious_features),
        'enhanced_verification_used': enhanced_verification_used
    }
    
    return render_template(
        'result.html',
        prediction_text=final_result,
        score=score,
        suspicious_features=display_suspicious_features,
        reasons=display_reasons,
        form_data=form_data,
        model_prediction=model_result,
        advanced_analysis=True,
        enhanced_verification_used=enhanced_verification_used,
        verification_details=verification_details,
        critical_issues_count=critical_issues_count
    )

@app.route('/scrape_linkedin', methods=['POST'])
def scrape_linkedin():
    url = request.form.get('linkedin_url')
    if not url:
        return jsonify({"error": "No LinkedIn URL provided"}), 400
    
    try:
        job_data = scrape_linkedin_job(url)
        return jsonify(job_data)
    except Exception as e:
        logging.error(f"Error scraping LinkedIn job: {str(e)}")
        return jsonify({"error": f"Failed to scrape job: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)