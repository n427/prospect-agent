import csv, json, time
from email_generator import generate_emails
from datetime import datetime

def run_pipeline(input_csv: str, output_csv: str):
    results = []

    with open(input_csv) as f:
        leads = list(csv.DictReader(f))

    print(f'Processing {len(leads)} leads...')

    for i, lead in enumerate(leads):
        print(f'\n[{i+1}/{len(leads)}] {lead["company_name"]}')
        try:
            result = generate_emails(
                lead['company_name'],
                lead['website'],
                lead.get('contact_name', 'Founder')
            )
            emails = result['emails']
            results.append({
                'company': lead['company_name'],
                'contact': lead.get('contact_name', ''),
                'status': 'success',
                'subject_direct': emails['direct']['subject'],
                'body_direct': emails['direct']['body'],
                'subject_curiosity': emails['curiosity']['subject'],
                'body_curiosity': emails['curiosity']['body'],
                'subject_pain': emails['pain']['subject'],
                'body_pain': emails['pain']['body'],
            })
        except Exception as e:
            print(f' ERROR: {e}')
            results.append({'company': lead['company_name'], 'status': f'error: {e}'})


    if results:
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f'\nDone. Results saved to {output_csv}')
        
if __name__ == '__main__':
    run_pipeline('leads.csv', 'outreach_results.csv')