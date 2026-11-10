"""Quick answers on the notification pages, and notification pages for the live exams that had none (Anil, 4 Nov 2026:
"upload the notifications on site on respective exams ... also masala questions like ... is the APPSC group-1 date extended?
... for all other exams").

apply(NOTIFS) adds 'faqs' (question, answer) lists to the existing pages and adds the new pages. notif_page() in build.py shows
them as "Quick answers" (FAQPage data too). Facts as of 4 November 2026; research notes with every source are in the project
doc claude/exam-news-pages.md. Where only news or coaching sites report something, the answer says so.

Update these answers when a board announces something (hall tickets, keys, extensions, exam dates).
"""
import os

ASOF = '4 November 2026'
UPSC_CAL = 'https://upsc.gov.in/sites/default/files/Calendar-Year-2027-Engl-200526.pdf'
TG_HM = ('https://websitenew.tgpsc.gov.in/preview/UFJFU1NOT1RFL05PVElGTi5fMDQtT0ctSE0tMjAyNi1NQU5BR0VSSE1XU1NCMjAyNjA5MTgxNzQ4MDEucGRm'
         'YWNjZXNzdGltZT0yMDI2LTEyLTE4r95v17a0y2d8i13v')
TG_AMVI = 'https://websitenew.tgpsc.gov.in/preview/RElSRUNUUkVDUlVJVE1FTlROT1RJLzMxLTIwMjItQU1WSS1OT1RJRk4yMDIyMTIzMTIwNTAzMi5wZGY=r95v17a0y2d8i13v'

# ---------------------------------------------------------------- Quick answers on the existing pages
FAQS = {
  'appsc-group-2-notification-2026.html': [
    ('Is the APPSC Group 2 notification 2026 out?', 'Yes. APPSC issued the brief notification No. 37/2026 on 13 October 2026 for 686 Group-II posts. The detailed notification (fee, age limits, reservations) is expected by 10 November 2026.'),
    ('When can I apply for APPSC Group 2 2026?', 'From 10 November to 30 November 2026 (till 11:59 pm) on psc.ap.gov.in, after creating or updating your One Time Profile Registration (OTPR).'),
    ('Has the APPSC Group 2 last date been extended?', 'No. The brief notification gives 10 to 30 November 2026 for online applications, and no change to that window had been announced as of 10 November 2026.'),
    ('When is the APPSC Group 2 screening test 2026?', 'Not announced yet. APPSC will give the date later, usually in a web note. In the last recruitment the screening test came about two months after the notification (25 February 2024).'),
    ('How many Deputy Tahsildar posts are there in Group 2 2026?', '200 Deputy Tahsildar posts and 176 Deputy MPDO posts, out of 686 in all.'),
    ('Is the Group 2 exam pattern changed?', 'No. The brief notification keeps the pattern of Notification 11/2023: a 150-mark screening test, then two 150-mark Mains papers. Selection is on the Mains marks.'),
    ('Is there negative marking in APPSC Group 2?', 'Yes. In the last Group 2 recruitment one-third of a mark was deducted for each wrong answer. The detailed 2026 notification will confirm it.'),
    ('What is the APPSC Group 2 fee?', 'The 2026 fee comes with the detailed notification. In 2023 it was ₹250 application fee + ₹80 exam fee; SC, ST, BC, PwBD, ex-service, white-card and unemployed AP candidates paid only ₹250.'),
  ],
  'appsc-group-1-notification-2026.html': [
    ('Can I still apply for APPSC Group 1 2026?', 'No. Applications for Group-I Services (Notification 07/2026) closed on 9 November 2026 at 11:59 pm. The last date had been extended once, from 27 October, and APPSC\'s web note said there would be no further extension.'),
    ('When is the APPSC Group 1 screening test 2026?', 'Tentatively on 24 January 2027 (Paper I and Paper II). The extension of the last date did not change it.'),
    ('When will the APPSC Group 1 hall ticket come?', 'Not announced yet. APPSC usually releases hall tickets on psc.ap.gov.in about one to two weeks before the exam, so expect them in January 2027. You need your OTPR ID and password to download it.'),
    ('How many posts are there in APPSC Group 1 2026?', '166. The brief notification (15 September 2026) said 163; the detailed notification of 6 October 2026 added one Deputy Collector, one Deputy Registrar and one Assistant Audit Officer post.'),
    ('What is the APPSC Group 1 application fee?', '₹250 application processing fee plus ₹120 examination fee (the exam fee is waived for the categories listed in the notification).'),
    ('Is there negative marking in the Group 1 screening test?', 'Yes. One-third of a mark is deducted for each wrong answer in both screening papers.'),
    ('Do Group 1 prelims marks count in the final merit?', 'No. The screening test only shortlists about 50 candidates per post for the Mains. The final merit is the Mains (750 marks) plus the interview (75 marks).'),
    ('I did OTPR but have no password. What do I do?', 'APPSC does not send one. Create it once on the candidate New User page with your OTPR ID (AP followed by 10 digits) and mobile number: 8 to 12 characters with a capital letter, a number and a special character. You will need it for the hall ticket.'),
  ],
  'appsc-analyst-grade-2-notification-2026.html': [
    ('Can I still apply for APPSC Analyst Grade-II?', 'The notification gave 13 October to 2 November 2026 (11:59 pm). A coaching website (Adda247) lists Analyst Grade-II among the APPSC posts whose last date was extended to 12 November 2026, but we could not confirm it from APPSC; check the candidate login on psc.ap.gov.in.'),
    ('When is the APPSC Analyst Grade-II exam?', 'Not announced yet. It will be a computer-based test (CBRT); APPSC will publish the date in a web note and the hall ticket.'),
    ('How many Analyst Grade-II posts are there?', '18, in the A.P. Pollution Control Board, under Notification 21/2026 of 13 October 2026.'),
    ('Who can apply for APPSC Analyst Grade-II?', 'Graduates in Chemistry, Biochemistry, Biology or Environmental Sciences, aged 18 to 44 on 1 July 2026 (with the usual relaxations).'),
    ('Is there negative marking in the Analyst Grade-II exam?', 'Yes. One-third of a mark is deducted for each wrong answer.'),
    ('What is the Analyst Grade-II salary?', 'Pay scale ₹48,440 – ₹1,37,220 a month.'),
  ],
  'appsc-assistant-environmental-engineer-notification-2026.html': [   # added 8 Nov 2026 (ASOF_PAGE)
    ('Can I still apply for APPSC Assistant Environmental Engineer?', 'The application window was 6 to 27 October 2026 (11:59 pm). We had not seen an extension notice for Notification 08/2026 as of 8 November 2026; check psc.ap.gov.in.'),
    ('When is the APPSC Assistant Environmental Engineer exam?', 'Not announced yet. It will be a computer-based test (CBRT); APPSC will publish the date in a web note and the hall ticket.'),
    ('How many Assistant Environmental Engineer posts are there?', '41, including 1 carried forward, in the A.P. Pollution Control Board, under Notification 08/2026 of 6 October 2026.'),
    ('Who can apply for APPSC Assistant Environmental Engineer?', 'B.E./B.Tech. graduates in Civil, Mechanical, Chemical or Environmental Engineering (or AMIE Civil, Sections A and B), aged 18 to 44 on 1 July 2026 (with the usual relaxations).'),
    ('Is there negative marking in the Assistant Environmental Engineer exam?', 'Yes. One-third of a mark is deducted for each wrong answer.'),
    ('What is the Assistant Environmental Engineer salary?', 'Pay scale ₹57,100 – ₹1,47,760 a month.'),
  ],
  'appsc-fro-notification-2026.html': [
    ('Is the APPSC FRO last date extended?', 'Yes, as reported: from 5 November to 12 November 2026, 11:59 pm (Adda247 and Career Power). The EO Grade-III last date moved to the same day (Sakshi Education). We could not read APPSC\'s own web note, so apply well before 12 November.'),
    ('How many Forest Range Officer posts are there in 2026?', '5, including 1 carried forward (Notification 16/2026, 16 October 2026).'),
    ('What is the age limit for APPSC FRO?', '18 to 30 years on 1 July 2026, with the usual relaxations for reserved categories.'),
    ('When is the APPSC FRO exam 2026?', 'Not announced yet. It will be computer-based (CBRT); APPSC will announce the date later.'),
    ('Is there negative marking in APPSC FRO?', 'Yes. One-third of a mark is deducted for each wrong answer.'),
    ('Is there a walking test for FRO?', 'Yes. Candidates picked in the ratio 1:3 after the written test take a walking test and a medical test, and a qualifying Computer Proficiency Test.'),
  ],
  'appsc-eo-grade-3-notification-2026.html': [
    ('What is the last date for APPSC EO Grade-III?', '12 November 2026. The last date for Notification 23/2026 was first 5 November and has been extended to 12 November 2026 (Sakshi Education, 10 November 2026). Apply early: the website slows down on the last day.'),
    ('Is the APPSC EO last date extended again?', 'Only once, from 5 to 12 November 2026, as reported on 10 November 2026. Do not count on another extension.'),
    ('How many EO Grade-III posts are there?', '104, district-wise, in the A.P. Endowments Subordinate Service.'),
    ('Can a non-Hindu apply for APPSC EO Grade-III?', 'No. Under Section 29(3) of the A.P. Endowments Act, 1987, the Executive Officer must be a person professing the Hindu religion.'),
    ('When is the APPSC EO Grade-III exam?', 'Not announced yet. It will be computer-based (CBRT): Paper I General Studies & Mental Ability and Paper II Hindu Philosophy & Temple System, 150 marks each.'),
    ('Is there negative marking in the EO exam?', 'Yes. One-third of a mark is deducted for each wrong answer.'),
    ('What is the EO Grade-III salary?', 'Pay scale ₹25,220 – ₹80,910 a month.'),
  ],
  'ap-police-si-notification-2026.html': [
    ('Has the AP Police SI 2026 online application started?', 'Not yet, as far as we could find on 10 November 2026. SLPRB says it will announce the application dates in a press note on slprb.ap.gov.in.'),
    ('When is the AP Police SI exam 2026?', 'The Preliminary Written Test date has not been announced yet.'),
    ('How many SI posts are there in AP Police 2026?', '378: 253 SCT SI (Civil), 116 SCT Reserve SI (AR) and 9 SI in the Special Protection Force. SI (Communications) and SI (PTO) have a separate notification.'),
    ('What is the age limit for AP SI 2026?', '21 to 27 years on 1 July 2026 (born between 2 July 1999 and 1 July 2005), relaxed by up to 5 years for SC, ST, BC and EWS candidates.'),
    ('Is there negative marking in the AP SI prelims?', 'No. No marks are deducted for wrong answers in the AP Police SI written tests.'),
    ('What are the qualifying marks for AP SI?', '40% for OC (and EWS), 35% for BC and 30% for SC and ST, in each paper.'),
  ],
  'ap-police-constable-notification-2026.html': [
    ('Has the AP Police Constable 2026 application started?', 'Not yet, as far as we could find on 10 November 2026. SLPRB will announce the online application dates in a press note on slprb.ap.gov.in.'),
    ('When is the AP Constable exam 2026?', 'The Preliminary Written Test date has not been announced yet.'),
    ('How many AP Police Constable posts are there in 2026?', '1,156 in this notification: 542 SCT PC (Civil), 285 SCT PC (AR), 158 Firemen, 150 Warders (Men) and 21 Warders (Women).'),
    ('What is the age limit for AP Constable 2026?', '18 to 24 years on 1 July 2026 for PC (Civil) and (AR), with the usual relaxations.'),
    ('Is there negative marking in the AP Constable exam?', 'No. No marks are deducted for wrong answers.'),
    ('Do the prelims marks count for selection?', 'No. The Preliminary Written Test is only qualifying (40% OC, 35% BC, 30% SC/ST). Selection is on the Final Written Examination.'),
  ],
  'ts-police-si-exam-date-hall-ticket-2026.html': [
    ('Is the TS Police SI exam postponed?', 'No postponement had been announced as of 10 November 2026. The Preliminary Written Test stays on Sunday, 29 November 2026, forenoon (marked tentative in TGPRB\'s press note of 17 September 2026).'),
    ('When will the TS SI hall ticket 2026 come?', 'TGPRB has not announced it yet. In 2022 the window opened 8 days before the exam, so expect it around 21 November 2026 on www.tgprb.in.'),
    ('What is the TS SI exam timing?', 'Forenoon. In 2022 it ran from 10 am to 1 pm; TGPRB has not announced the 2026 timing yet. Gates close at the start time.'),
    ('Is there negative marking in the TS SI prelims?', 'Yes. 0.2 of a mark is deducted for each wrong answer; an unanswered question gets zero.'),
    ('What are the qualifying marks for TS SI prelims?', '60 out of 200 for OC/EWS (30%), 50 for BC (25%), 40 for SC, ST and Ex-Servicemen (20%).'),
    ('How many applied for TS SI 2026?', 'About 1.6 lakh applications for 275 posts.'),
    ('Do the prelims marks count in the final selection?', 'No. The prelims only qualifies you for the physical tests; selection is on the Final Written Examination.'),
  ],
  'ts-police-si-answer-key-2026.html': [
    ('When will the TS SI answer key 2026 come?', 'After the exam on 29 November 2026. In 2022 the preliminary key came 5 days after the exam, so expect it in early December 2026 on www.tgprb.in.'),
    ('How do I raise an objection to the TS SI key?', 'In your candidate login on www.tgprb.in, question by question, during the objection window TGPRB announces with the key (three days in 2022).'),
    ('Is there a cut-off in the TS SI prelims?', 'No. Everyone who gets the qualifying mark of their category (60/50/40 out of 200) goes on to the physical tests.'),
    ('How many marks are needed to pass the TS SI prelims?', '60 for OC/EWS, 50 for BC, 40 for SC, ST and Ex-Servicemen, after the 0.2 negative mark.'),
    ('What was the highest score in the 2022 TS SI prelims?', '133 out of 200; the average was 47.25 and 46.8% of candidates qualified.'),
  ],
  'ts-police-constable-exam-date-hall-ticket-2026.html': [
    ('Is the TS Police Constable exam postponed?', 'No postponement had been announced as of 10 November 2026. The Preliminary Written Test stays on Sunday, 20 December 2026, forenoon (tentative).'),
    ('When will the TS Constable hall ticket 2026 come?', 'Not announced yet. In 2022 the window opened 10 days before the exam, so expect it around 10 December 2026 on www.tgprb.in.'),
    ('How many posts are there in TS Police Constable 2026?', '7,112, including 3,697 PC (Civil), 1,052 PC (AR), 1,380 TGSP constables and 751 Fire Fighters.'),
    ('Is there negative marking in the TS Constable exam?', 'Yes. 0.2 of a mark is deducted for each wrong answer.'),
    ('What are the qualifying marks for TS Constable prelims?', '60 out of 200 for OC/EWS, 50 for BC, 40 for SC, ST, Ex-Servicemen and Home Guards.'),
    ('How many applied for TS Constable 2026?', 'About 3.9 lakh applications.'),
  ],
  'ts-police-constable-answer-key-2026.html': [
    ('When will the TS Constable answer key 2026 come?', 'After the exam on 20 December 2026. In 2022 the preliminary key came two days after the exam, so expect it a few days after 20 December on www.tgprb.in.'),
    ('Is there a cut-off in the TS Constable prelims?', 'No. Everyone who reaches the qualifying mark (60/50/40 out of 200) goes on to the physical tests.'),
    ('What was the highest score in the 2022 TS Constable prelims?', '141 out of 200; the average was 41.16 and 31.4% qualified.'),
  ],
}

# ---------------------------------------------------------------- new notification pages
NEW = {
  'upsc-cse-2027-notification.html': dict(
    exam='upsc-prelims', board='UPSC', site='upsc.gov.in', crumb='CSE 2027 Notification',
    title='UPSC CSE 2027 Notification (13 January), Prelims Date 23 May 2027, Eligibility, Attempts, Pattern & PYQs | Learn with Anil',
    desc='UPSC Civil Services 2027: notification scheduled for 13 January 2027, apply by 2 February, Prelims on Sunday 23 May 2027 and Mains from 20 August 2027 '
         '(UPSC Calendar 2027). Age 21–32, attempts, fee, the Prelims and Mains pattern, CSE 2026 vacancies, and previous year papers with answers.',
    h1='UPSC CSE 2027: Prelims on Sunday, 23 May 2027',
    lede='UPSC\'s Calendar of Examinations 2027 schedules the Civil Services (Preliminary) Examination 2027 for Sunday, 23 May 2027. The notification is due on '
         '13 January 2027 with applications until 2 February 2027, and the Mains begin on 20 August 2027. Vacancies come with the notification. Below: the dates, '
         'eligibility and attempts, the pattern, and the Prelims and Mains previous papers.',
    hi='UPSC सिविल सेवा (प्रारंभिक) परीक्षा 2027: रविवार, 23 मई 2027। अधिसूचना 13 जनवरी 2027 को, आवेदन 2 फरवरी 2027 तक, मुख्य परीक्षा 20 अगस्त 2027 से (UPSC कैलेंडर 2027)।',
    pdf=UPSC_CAL, pdfname='UPSC Calendar of Examinations / Recruitment Tests 2027 (issued May 2026)',
    more_src=[('https://www.freepressjournal.in/education/upsc-releases-2027-examination-calendar-civil-services-prelims-on-may-23-mains-from-august-20-download-pdf-now', 'Free Press Journal, UPSC 2027 calendar'),
              ('https://www.deccanchronicle.com/education/upsc-issues-civil-services-examination-2026-notification-933-vacancies-announced-1934923', 'Deccan Chronicle, CSE 2026 notification (933 vacancies)'),
              ('https://www.upsc.gov.in/sites/default/files/WR-CSM-2026-Engl-RollList-05112026.pdf', 'UPSC, CSE Mains 2026 result (roll-number list, 5 November 2026)')],
    related=['upsc-capf-2027-notification.html', 'upsc-epfo-apfc-2026-notification.html'],
    no_practice=True,
    sections=[
      ('Important dates (UPSC Calendar 2027)', 'table', [
        ('Notification', '13 January 2027 (scheduled)'), ('Last date to apply', '2 February 2027'),
        ('Preliminary Examination', 'Sunday, 23 May 2027 (one day; also the IFoS screening)'), ('Main Examination', 'From 20 August 2027 (5 days)'),
        ('Vacancies', 'Announced with the notification'), ('Apply at', 'upsconline.gov.in')]),
      ('', 'note', 'UPSC\'s calendar says the dates can change. In 2026 the notification came out on 4 February 2026, about three weeks after its calendar date, '
                   'while the Prelims stayed on the calendar date (24 May 2026). So plan for 23 May 2027, but watch upsc.gov.in for the notification.'),
      ('CSE 2026 for reference', 'table', [
        ('Notification', '4 February 2026'), ('Vacancies', 'About 933 (including 33 for persons with benchmark disabilities)'),
        ('Prelims', '24 May 2026'), ('Qualified for the Mains', '13,343 (result of June 2026)'), ('Mains', 'Began 21 August 2026'), ('Mains result', '5 November 2026: 2,526 candidates qualified for the interview (personality test); interview dates to be announced')]),
      ('Who can apply (CSE 2026 rules; the 2027 notification will confirm)', 'list', [
        'A bachelor\'s degree from a recognised university. Final-year students may apply for the Prelims but must pass before the Mains application.',
        'Age 21 to 32 years on 1 August of the exam year, with 5 more years for SC/ST, 3 for OBC (non-creamy layer) and 10 for persons with benchmark disabilities.',
        'Attempts: 6 for General/EWS, 9 for OBC and PwBD, no limit for SC/ST up to the upper age limit.',
        'Fee ₹100; women, SC, ST and PwBD candidates pay nothing.']),
      ('Exam pattern', 'table+', (['Stage', 'Papers', 'Marks'], [
        ('Prelims Paper I', 'General Studies: 100 questions, 2 hours', '200 (counts for the Prelims cut-off)'),
        ('Prelims Paper II (CSAT)', '80 questions, 2 hours', '200 (qualifying: 33%)'),
        ('Mains', 'Essay, GS I–IV, Optional Papers I–II (250 each) + two qualifying language papers', '1,750'),
        ('Interview (Personality Test)', '', '275'), ('Final merit', 'Mains + Interview', '2,025')])),
      ('', 'note', 'One-third of the marks of a question is deducted for each wrong answer in both Prelims papers, including CSAT.'),
      ('Start with the previous papers', 'html',
       '<p>Practise the real UPSC papers with UPSC\'s answer keys and explanations in English and Hindi: '
       '<a href="/upsc-prelims/pyqs.html">UPSC Prelims GS and CSAT previous papers</a> · <a href="/upsc-cse/mains-pyqs/">UPSC Mains GS 1–4 PYQs with free model answers</a> · '
       '<a href="/upsc-cse/">UPSC CSE hub</a></p>'),
    ],
    faqs=[
      ('Is the UPSC CSE 2027 notification out?', 'No, not as of 10 November 2026. UPSC\'s Calendar 2027 schedules it for 13 January 2027. In 2026 the notification came about three weeks after its calendar date, so a short delay is possible.'),
      ('When is UPSC Prelims 2027?', 'Sunday, 23 May 2027, as per UPSC\'s Calendar 2027.'),
      ('Has the UPSC 2027 exam date changed?', 'No change has been announced as of 4 November 2026. UPSC says calendar dates can change if circumstances require, so check upsc.gov.in.'),
      ('When does UPSC Mains 2027 start?', '20 August 2027, over 5 days.'),
      ('What is the last date to apply for UPSC CSE 2027?', '2 February 2027 as per the calendar; the notification will give the final date.'),
      ('How many vacancies are there in UPSC CSE 2027?', 'Not announced yet; they come with the notification. CSE 2026 had about 933 (CSE 2025: 979).'),
      ('Is the UPSC Mains 2026 result out?', 'Yes. UPSC declared the CSE Mains 2026 result on 5 November 2026: 2,526 candidates qualified for the personality test (interview). UPSC will announce the interview schedule and e-summon letters on upsc.gov.in.'),
      ('How many attempts are allowed in UPSC CSE?', '6 for General and EWS, 9 for OBC and PwBD, and no limit for SC/ST up to the upper age limit (37).'),
      ('Is there negative marking in CSAT?', 'Yes. One-third of the question\'s marks is deducted for a wrong answer in both GS Paper I and CSAT. CSAT is only qualifying (33%), but wrong answers can still make you fail it.'),
    ]),
  'upsc-capf-2027-notification.html': dict(
    exam='upsc-capf', board='UPSC', site='upsc.gov.in', crumb='CAPF AC 2027 Notification',
    title='UPSC CAPF AC 2027 Notification (17 February), Exam Date 4 July 2027, Age Limit, Pattern & Previous Papers | Learn with Anil',
    desc='UPSC CAPF (Assistant Commandants) 2027: notification scheduled for 17 February 2027, apply by 9 March, exam on Sunday 4 July 2027 (UPSC Calendar 2027). '
         'Age 20–25, fee, Paper I and Paper II pattern with negative marking, 2026 vacancies (349) and CAPF previous year papers with answers in English and Hindi.',
    h1='UPSC CAPF AC 2027: exam on Sunday, 4 July 2027',
    lede='UPSC\'s Calendar 2027 schedules the Central Armed Police Forces (Assistant Commandants) Examination 2027 for Sunday, 4 July 2027, earlier than in 2026 '
         '(19 July). The notification is due on 17 February 2027, with applications until 9 March 2027. Below: the dates, eligibility, the pattern, the 2026 vacancies '
         'and the CAPF previous papers.',
    hi='UPSC CAPF (असिस्टेंट कमांडेंट) परीक्षा 2027: रविवार, 4 जुलाई 2027। अधिसूचना 17 फरवरी 2027 को, आवेदन 9 मार्च 2027 तक (UPSC कैलेंडर 2027)।',
    pdf=UPSC_CAL, pdfname='UPSC Calendar of Examinations / Recruitment Tests 2027 (issued May 2026)',
    more_src=[('https://news.careers360.com/upsc-exam-calendar-2027-out-upsc-gov-in-cse-ifs-prelims-on-may-23-recruitment-exam-nda-na-cds-ii/amp', 'Careers360, UPSC 2027 calendar'),
              ('https://www.freepressjournal.in/education/want-to-apply-for-upsc-capf-2026-registration-begins-for-349-assistant-commandant-post-now-at-upsconlinenicin-check-details-here', 'Free Press Journal, CAPF 2026 (349 posts)')],
    related=['upsc-cse-2027-notification.html', 'upsc-epfo-apfc-2026-notification.html'],
    sections=[
      ('Important dates (UPSC Calendar 2027)', 'table', [
        ('Notification', '17 February 2027 (scheduled)'), ('Last date to apply', '9 March 2027'), ('Written examination', 'Sunday, 4 July 2027'),
        ('Vacancies', 'Announced with the notification'), ('Apply at', 'upsconline.gov.in')]),
      ('CAPF 2026 for reference', 'table', [
        ('Notification', '20 February 2026'), ('Written examination', '19 July 2026'),
        ('Vacancies', '349: BSF 108, CRPF 106, CISF 70, SSB 53, ITBP 12')]),
      ('Who can apply (2026 rules; the 2027 notification will confirm)', 'list', [
        'A bachelor\'s degree from a recognised university; final-year students may apply.',
        'Age 20 to 25 years on 1 August of the exam year; 5 more years for SC/ST, 3 for OBC, and relaxations for ex-servicemen and central government servants.',
        'Men and women can apply. Physical standards (2026): men 165 cm, chest 81 cm with 5 cm expansion, 50 kg; women 157 cm, 46 kg.',
        'Fee ₹200; women, SC and ST candidates pay nothing.']),
      ('Exam pattern', 'table+', (['Paper', 'Type', 'Marks · time'], [
        ('Paper I: General Ability and Intelligence', 'Objective (MCQ)', '250 · 2 hours, 10 am – 12 noon'),
        ('Paper II: General Studies, Essay and Comprehension', 'Descriptive', '200 · 3 hours, 2 – 5 pm'),
        ('Physical tests and medical', 'Qualifying', '—'), ('Interview / Personality Test', '', '150')])),
      ('', 'note', 'Negative marking: one-third of the marks of a question for each wrong answer, in Paper I only. Paper II is evaluated only for candidates who reach the Paper I minimum.'),
    ],
    faqs=[
      ('Is the UPSC CAPF 2027 notification out?', 'No, not as of 4 November 2026. It is scheduled for 17 February 2027 in UPSC\'s Calendar 2027.'),
      ('When is the UPSC CAPF AC 2027 exam?', 'Sunday, 4 July 2027.'),
      ('Has the CAPF 2027 exam date changed?', 'No change has been announced as of 4 November 2026. Note it is two weeks earlier than the 2026 exam (19 July 2026).'),
      ('What is the last date to apply for CAPF 2027?', '9 March 2027 as per the calendar.'),
      ('How many vacancies are there in CAPF 2027?', 'Not announced yet. CAPF 2026 had 349 (BSF 108, CRPF 106, CISF 70, SSB 53, ITBP 12).'),
      ('What is the age limit for UPSC CAPF AC?', '20 to 25 years on 1 August of the exam year, plus 5 years for SC/ST and 3 for OBC.'),
      ('Is there negative marking in UPSC CAPF?', 'Yes, one-third of the question\'s marks in Paper I (objective). Paper II is descriptive.'),
      ('Can women apply for UPSC CAPF AC?', 'Yes. Women are eligible and pay no fee.'),
    ]),
  'upsc-epfo-apfc-2026-notification.html': dict(
    exam='upsc-epfo', board='UPSC', site='upsc.gov.in', crumb='EPFO APFC 2026',
    title='UPSC EPFO APFC 2026: Exam on 20 December, 80 Posts, Admit Card, Pattern – and Is the EO/AO Notification Out? | Learn with Anil',
    desc='UPSC EPFO 2026: Assistant Provident Fund Commissioner (APFC), 80 posts (Special Advt. 52/2026), Recruitment Test on Sunday 20 December 2026. Admit card, '
         'pattern (120 Q, 300 marks, 1/3 negative), age, interview weightage 75:25, the EO/AO and PA status, and EPFO previous papers with answers.',
    h1='UPSC EPFO APFC 2026: Recruitment Test on Sunday, 20 December',
    lede='UPSC\'s EPFO notification for 2026 is for Assistant Provident Fund Commissioner only: 80 posts under Special Advertisement No. 52/2026 (August 2026). '
         'Applications closed on 14 September 2026 and the pen-and-paper Recruitment Test is on Sunday, 20 December 2026. There is no EO/AO or PA advertisement this year. '
         'Below: the dates, the pattern, eligibility and the EPFO previous papers.',
    hi='UPSC EPFO APFC 2026: 80 पद (विशेष विज्ञापन 52/2026), भर्ती परीक्षा रविवार, 20 दिसंबर 2026। इस वर्ष EO/AO या PA का कोई विज्ञापन नहीं।',
    pdf='https://upsc.gov.in/sites/default/files/AdvtNo-52-2026-Special-Engl-210826.pdf', pdfname='UPSC Special Advertisement No. 52/2026 (APFC, EPFO), August 2026',
    more_src=[('https://www.freepressjournal.in/education/upsc-epfo-apfc-recruitment-2026-notification-out-for-80-posts-at-upscgovin-apply-from-august-22', 'Free Press Journal, APFC 2026 (80 posts)'),
              ('https://prepp.in/upsc-epfo-exam', 'Prepp, EPFO 2026 dates and the EO/AO status')],
    related=['upsc-cse-2027-notification.html', 'upsc-capf-2027-notification.html'],
    sections=[
      ('Important dates', 'table', [
        ('Advertisement', 'Special Advt. No. 52/2026, August 2026'), ('Online applications', '22 August to 14 September 2026 (extended from 11 September; closed)'),
        ('Recruitment Test', 'Sunday, 20 December 2026, pen and paper (OMR)'), ('Admit card', 'On upsc.gov.in before the test (usually 1–3 weeks before); not sent by post'),
        ('Interview', 'After the test result')]),
      ('Posts', 'table', [
        ('Post', 'Assistant Provident Fund Commissioner, EPFO (Ministry of Labour & Employment)'), ('Vacancies', '80: UR 29, EWS 8, OBC 18, SC 15, ST 10'),
        ('Pay', 'Level 10 of the pay matrix (₹56,100 basic)')]),
      ('Who could apply', 'list', [
        'A bachelor\'s degree from a recognised university (a diploma in Company Law, Labour Laws or Public Administration is desirable).',
        'Maximum age 35 for UR/EWS, 38 for OBC and 40 for SC/ST, with further relaxations in the advertisement.',
        'Fee ₹25; women, SC, ST and PwBD candidates paid nothing.']),
      ('Exam pattern', 'table+', (['Stage', 'Details', 'Marks'], [
        ('Recruitment Test', '120 objective questions, 2 hours, Hindi and English (General English in English only)', '300 (2.5 per question)'),
        ('Interview', '', '100'), ('Final merit', 'Test 75% : Interview 25%', '—')])),
      ('', 'note', 'Negative marking: one-third of a question\'s marks is deducted for each wrong answer; a blank answer loses nothing.'),
      ('EO/AO and PA', 'list', [
        'Enforcement Officer / Accounts Officer: no advertisement in 2026. The last EO/AO recruitment was Advt. 52/2025 (test 30 November 2025, common with APFC).',
        'Personal Assistant: the latest is still Advt. 51/2024 (323 posts, test 7 July 2024). UPSC published its answer key in September 2026.',
        'The EO/AO and APFC papers test the same syllabus, so every EPFO paper on this site is useful practice for 20 December.']),
    ],
    faqs=[
      ('Is the UPSC EPFO notification 2026 out?', 'Yes, but only for APFC: 80 posts under Special Advertisement No. 52/2026 (August 2026). Applications closed on 14 September 2026.'),
      ('When is the UPSC EPFO APFC exam 2026?', 'Sunday, 20 December 2026, pen and paper.'),
      ('Is the EPFO APFC admit card out?', 'Not as of 4 November 2026. UPSC puts the e-admit card on upsc.gov.in a little before the test, usually 1–3 weeks before.'),
      ('Is the EPFO EO/AO notification 2026 out?', 'No. UPSC has not advertised EO/AO posts in 2026. Coaching sites report that EPFO withdrew its request for 311 EO/AO posts in June 2026; we have not seen an official notice on it.'),
      ('Can I still apply for UPSC APFC 2026?', 'No. Applications closed on 14 September 2026 after an extension from 11 September.'),
      ('Is there negative marking in the UPSC EPFO exam?', 'Yes. One-third of the question\'s marks is deducted for each wrong answer.'),
      ('What is the UPSC EPFO APFC exam pattern?', '120 objective questions for 300 marks in 2 hours, then a 100-mark interview; the final merit weighs the test 75% and the interview 25%.'),
      ('Is the UPSC EPFO 2025 answer key out?', 'Not as of 25 October 2026. UPSC usually publishes keys only after the whole recruitment is over (the PA 2024 key came in September 2026).'),
    ]),
  'ssc-cgl-2026-notification.html': dict(
    exam='ssc-cgl', board='SSC', site='ssc.gov.in', crumb='SSC CGL 2026 Status',
    title='SSC CGL 2026: Tier 1 Answer Key Out (4 November), Result Status, Tier 2 Date, 10,731 Vacancies, Pattern & Previous Papers | Learn with Anil',
    desc='SSC CGL 2026: notified 21 May 2026, about 10,731 vacancies (revised), Tier-I held 30 September – 30 October 2026. Answer key and result status, Tier-II '
         '(tentatively December 2026), negative marking, age limits by post, and SSC CGL previous year papers with answers.',
    h1='SSC CGL 2026: Tier 1 is over. Answer key, result and Tier 2',
    lede='The SSC CGL 2026 Tier-I computer-based exam ran from 30 September to 30 October 2026. Next come the Tier-I answer key with objections, then the result, '
         'then Tier-II, which is tentatively in December 2026. The Tier-I answer key came out on 4 November 2026. Below: the status as of 10 November 2026, the vacancies, the pattern and the CGL previous papers.',
    hi='SSC CGL 2026: टियर-I परीक्षा 30 सितंबर – 30 अक्टूबर 2026 तक हुई। अब उत्तर कुंजी, परिणाम और फिर टियर-II (संभावित दिसंबर 2026)।',
    pdf='https://ssc.gov.in/', pdfname='Staff Selection Commission notices, ssc.gov.in (CGL 2026 notice of 21 May 2026 and the Tier-I schedule notice of 12 September 2026)',
    more_src=[('https://www.business-standard.com/amp/education/news/ssc-cgl-exam-date-2026-out-tier-1-from-sept-30-to-oct-30-check-notice-nc-126091400526_1.html', 'Business Standard, Tier-I schedule'),
              ('https://testbook.com/news/ssc-cgl-vacancy-2026-27-out/', 'Testbook, revised vacancies'),
              ('https://testbook.com/news/ssc-cgl-2026-answer-key-out/', 'Testbook, 5 November 2026: Tier-I answer key out 4 November, objections till 7 November'),
              ('https://www.freejobalert.com/articles/ssc-cgl-answer-key-2026-3078244', 'FreeJobAlert, 4 November 2026: Tier-I answer key released')],
    sections=[
      ('Where SSC CGL 2026 stands', 'table', [
        ('Notification', '21 May 2026'), ('Applications', '21 May to 25 June 2026 (closed); correction window 1–3 July'),
        ('Tier-I (CBT)', '30 September to 30 October 2026 (over)'), ('Tier-I answer key', 'Released 4 November 2026 with the response sheets; objections closed 7 November 2026 (as reported)'),
        ('Tier-I result', 'Not out yet; expected in December 2026 (coaching-site estimate, not an SSC date)'), ('Tier-II', 'Tentatively December 2026; exact date not announced'),
        ('Vacancies', 'About 10,731 (tentative; 12,256 at notification)')]),
      ('Exam pattern', 'table+', (['Stage', 'Details', 'Negative marking'], [
        ('Tier-I (qualifying)', 'Reasoning, General Awareness, Quantitative Aptitude, English: 25 questions each, 100 questions, 200 marks, 60 minutes', '0.5 per wrong answer'),
        ('Tier-II Paper I (all posts)', 'Maths 30 + Reasoning 30; English 45 + General Awareness 25; Computer 20 (qualifying); 3 marks a question', '1 per wrong answer'),
        ('Tier-II Session II', 'Data Entry Speed Test, 15 minutes', 'qualifying'),
        ('Tier-II Paper II / III', 'Statistics (JSO) / General Studies – Finance & Economics (AAO)', '0.5 per wrong answer')])),
      ('Who could apply', 'list', [
        'A bachelor\'s degree; JSO needs 60% in Class 12 Maths or Statistics in the degree, and SI (Statistics) needs Statistics as a subject.',
        'Age on 1 August 2026 by post: 18–27, 18–30, 20–30 or 18–32 years; relaxation OBC 3, SC/ST 5, PwBD 10 years.',
        'Fee ₹100; women, SC, ST, PwBD and ex-servicemen paid nothing.']),
    ],
    faqs=[
      ('Is the SSC CGL 2026 Tier 1 answer key out?', 'Yes. SSC released the Tier-I answer key with candidates\' response sheets on 4 November 2026 on ssc.gov.in. The objection window closed on 7 November 2026 (as reported).'),
      ('Is the SSC CGL 2026 Tier 1 result out?', 'Not as of 10 November 2026. It comes after SSC checks the objections; reports expect it in December 2026, but SSC has not given a date.'),
      ('When is SSC CGL Tier 2 2026?', 'SSC has not given an exact date. It is tentatively in December 2026.'),
      ('How many vacancies are there in SSC CGL 2026?', 'About 10,731 (tentative), revised from 12,256 at the notification.'),
      ('Is there negative marking in SSC CGL?', 'Yes. Tier-I: 0.5 mark per wrong answer. Tier-II Paper I: 1 mark per wrong answer (each question carries 3).'),
      ('Do Tier-I marks count in the final merit?', 'No. Tier-I only qualifies you for Tier-II; the final merit is on Tier-II.'),
      ('What is the SSC CGL age limit?', 'It depends on the post: 18–27, 18–30, 20–30 or 18–32 years on 1 August 2026.'),
      ('When will the SSC CGL 2027 notification come?', 'Not announced. It will appear in SSC\'s 2027-28 exam calendar, which is not out yet.'),
    ]),
  'appsc-amvi-notification-2026.html': dict(
    exam='appsc-amvi', board='APPSC', site='psc.ap.gov.in', crumb='AMVI Notification 2026',
    title='APPSC AMVI Notification 2026 – 50 Posts, Apply Online 6–26 November, Eligibility, Licence, Pattern & Previous Papers | Learn with Anil',
    desc='APPSC Assistant Motor Vehicle Inspector Notification 36/2026: 50 posts, online applications 6 to 26 November 2026, Mechanical/Automobile degree or '
         'Automobile diploma with a heavy licence, age 21–36, pay ₹48,440–1,37,220, CBRT pattern (450 marks, 1/3 negative) and APPSC AMVI previous papers.',
    h1='APPSC AMVI Notification 2026: 50 posts',
    lede='APPSC issued a brief notification (No. 36/2026, 13 October 2026) for 50 posts of Assistant Motor Vehicle Inspector in the A.P. Transport Service. '
         'Online applications run from 6 to 26 November 2026; the detailed notification gives the fee and relaxations. This is a new recruitment, separate from '
         'Notification 21/2025, whose exam was held in January 2026. Below: the dates, eligibility, the pattern and the AMVI previous papers.',
    te='APPSC అసిస్టెంట్ మోటార్ వెహికల్ ఇన్‌స్పెక్టర్ నోటిఫికేషన్ 36/2026: 50 పోస్టులు. ఆన్‌లైన్ దరఖాస్తులు నవంబర్ 6 నుంచి 26 వరకు.',
    pdf='https://psc.ap.gov.in/', pdfname='APPSC brief notification No. 36/2026 (Assistant Motor Vehicle Inspector), 13 October 2026, psc.ap.gov.in',
    more_src=[('https://cdn.testbook.com/1791965106384-APPSC%20Assistant%20Motor%20Vehicle%20Inspector%20Notification%202026.pdf/1791965108.pdf', 'copy of the notification PDF (Testbook)'),
              ('https://portal-psc.ap.gov.in/', 'APPSC portal: Notification 21/2025 result and selection')],
    sections=[
      ('Important dates', 'table', [
        ('Brief notification (No. 36/2026)', '13 October 2026'), ('Detailed notification', 'Due on or before 6 November 2026 (fee, relaxations, physical standards)'),
        ('Online applications', '6 November to 26 November 2026 (till 11:59 pm)'), ('Written examination', 'Computer-based (CBRT); date to be announced'),
        ('Official website', 'psc.ap.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Assistant Motor Vehicle Inspector, A.P. Transport Service'), ('Vacancies', '50 (provisional)'),
        ('Pay scale', '₹48,440 – ₹1,37,220'), ('Age', '21 to 36 years on 1 July 2026, with relaxations in the detailed notification')]),
      ('Who can apply', 'list', [
        'A degree in Mechanical or Automobile Engineering, or a Diploma in Automobile Engineering.',
        'A motor driving licence with at least 3 years\' driving experience and a Heavy Transport Vehicle endorsement. Women holding only an LMV licence must get the HTV endorsement within 2 years of joining.']),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I', 'General Studies & Mental Ability (degree standard)', '150 · 150 · 150 min'),
        ('Paper II', 'Automobile Engineering (diploma standard)', '150 · 300 · 150 min'),
        ('Total', 'One written exam, no screening test', '450')])),
      ('', 'note', 'Negative marking: one-third of the question\'s marks for each wrong answer. A Computer Proficiency Test scheme is attached; the detailed notification says whether it applies.'),
      ('The January 2026 AMVI exam (Notification 21/2025)', 'list', [
        'Notification 21/2025 (24 September 2025) was a limited recruitment for one carried-forward post. Its papers were held on 27 and 28 January 2026; these are the 2026 papers on this site.',
        'Final key and result: 23 April 2026. Selection: 20 May 2026. That recruitment is complete.']),
    ],
    faqs=[
      ('Is the APPSC AMVI 2026 notification out?', 'Yes. Brief notification No. 36/2026 of 13 October 2026, 50 posts.'),
      ('When can I apply for APPSC AMVI 2026?', 'From 6 November to 26 November 2026, 11:59 pm, on psc.ap.gov.in after OTPR.'),
      ('Is the APPSC AMVI exam date out?', 'No. The brief notification gives no exam date; APPSC will announce it later.'),
      ('Can diploma holders apply for APPSC AMVI?', 'Yes, with a Diploma in Automobile Engineering. A degree must be in Mechanical or Automobile Engineering.'),
      ('Is a heavy licence compulsory for AMVI?', 'Yes: a driving licence with 3 years\' experience and an HTV endorsement. Women with only an LMV licence get 2 years after joining to add the endorsement.'),
      ('Is there negative marking in APPSC AMVI?', 'Yes, one-third of the question\'s marks for each wrong answer.'),
      ('What was the January 2026 AMVI exam?', 'Notification 21/2025, for one carried-forward post. Its final key and result came on 23 April 2026 and the selection on 20 May 2026.'),
      ('What is the AMVI salary in AP?', '₹48,440 – ₹1,37,220 a month (pay scale).'),
    ]),
  'tgpsc-amvi-notification.html': dict(
    exam='tgpsc-amvi', board='TGPSC', site='websitenew.tgpsc.gov.in', crumb='AMVI Notification',
    title='TGPSC AMVI Notification 2026: Is It Out? Last Notification 31/2022 (113 Posts), Eligibility, Pattern & Previous Papers | Learn with Anil',
    desc='Telangana AMVI notification status: no new TGPSC Assistant Motor Vehicle Inspector notification in 2026 so far. The last one, 31/2022, had 113 posts; '
         'eligibility, heavy licence, physical standards, age 21–39, pay ₹45,960–1,24,150, 450-mark pattern and TG AMVI previous papers.',
    h1='TGPSC AMVI notification: none yet in 2026',
    lede='TGPSC has not issued an Assistant Motor Vehicle Inspector notification in 2026: none of the 11 notifications on its 2026 list is for AMVI (checked on '
         '4 November 2026). The last one was TSPSC Notification 31/2022 for 113 posts, whose exam was held in June 2023. Its rules are below, as the best guide to '
         'the next one, with the TG AMVI previous papers.',
    te='TGPSC అసిస్టెంట్ మోటార్ వెహికల్ ఇన్‌స్పెక్టర్: 2026లో ఇంకా కొత్త నోటిఫికేషన్ రాలేదు. చివరిది 31/2022 (113 పోస్టులు).',
    pdf=TG_AMVI, pdfname='TSPSC Notification No. 31/2022 (Assistant Motor Vehicle Inspector), 31 December 2022',
    more_src=[('https://websitenew.tgpsc.gov.in/notifications', 'TGPSC notifications list (2026)')],
    related=['tgpsc-hmwssb-manager-notification-2026.html'],
    sections=[
      ('Status', 'table', [
        ('New notification in 2026', 'None so far (TGPSC notifications list, 4 November 2026)'), ('Last notification', 'TSPSC No. 31/2022, 31 December 2022: 113 posts (Multi-Zone I 54, Multi-Zone II 59)'),
        ('Applications (31/2022)', '12 January to 1 February 2023'), ('Exam (31/2022)', 'Held 28 June 2023, computer-based'),
        ('Official website', 'websitenew.tgpsc.gov.in')]),
      ('Who could apply (31/2022)', 'list', [
        'A degree in Mechanical or Automobile Engineering, or a 3-year Diploma in Automobile Engineering.',
        'A valid heavy motor vehicle (transport) driving licence; women with only an LMV licence had 2 years after joining to get the heavy endorsement.',
        'Physical standards: men 165 cm and chest 86.3 cm (+5 cm); women 157.5 cm; lower for SC/ST. Eyesight 6/6.',
        'Age 21 to 39 years on 1 July 2022, plus 5 years for SC, ST, BC and EWS. Fee ₹200 + ₹120 exam fee (exam fee waived for the unemployed).']),
      ('Exam pattern (31/2022)', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I', 'General Studies & General Abilities (English and Telugu)', '150 · 150 · 150 min'),
        ('Paper II', 'Automobile Engineering, diploma level (English)', '150 · 300 · 150 min'), ('Total', '', '450')])),
      ('', 'note', 'Pay scale (31/2022): ₹45,960 – ₹1,24,150. The 31/2022 notification does not mention negative marking. Qualifying marks: 40% OC/EWS, 35% BC, 30% SC/ST.'),
    ],
    faqs=[
      ('Is the TGPSC AMVI notification 2026 out?', 'No. TGPSC\'s list of 2026 notifications (checked 4 November 2026) has no AMVI post.'),
      ('When was the last TG AMVI notification?', 'TSPSC Notification 31/2022, dated 31 December 2022, for 113 posts.'),
      ('When was the last TG AMVI exam held?', '28 June 2023, computer-based. Certificate verification followed in June 2024.'),
      ('Can a diploma holder apply for TG AMVI?', 'Yes. Under 31/2022 a 3-year Diploma in Automobile Engineering qualified, as did a Mechanical or Automobile Engineering degree.'),
      ('Is a heavy licence needed for TG AMVI?', 'Yes, a valid heavy motor vehicle (transport) licence.'),
      ('What is the TG AMVI salary?', '₹45,960 – ₹1,24,150 under 31/2022.'),
      ('Is there negative marking in TG AMVI?', 'The 31/2022 notification does not mention negative marking.'),
    ]),
  'tgpsc-hmwssb-manager-notification-2026.html': dict(
    exam='tgpsc-hmwssb-manager', board='TGPSC', site='websitenew.tgpsc.gov.in', crumb='HMWSSB Manager Notification 2026',
    title='TGPSC HMWSSB Manager (Engineering) Notification 2026 – 130 Posts, Exam in December, Hall Ticket, Pattern (450 Marks) & Previous Papers | Learn with Anil',
    desc='TGPSC Notification 04/OG/HM/2026: 130 Manager (Engineering) posts in HMWSSB. Applications closed 17 October 2026; exam tentatively in December 2026. '
         'Hall ticket, branch shares (80% Civil), age 18–44, fee, pay ₹54,220–1,33,630, Paper I 150 + Paper II 300 marks, no interview, and previous papers.',
    h1='TGPSC HMWSSB Manager 2026: 130 posts, exam in December',
    lede='TGPSC notified 130 posts of Manager (Engineering) in the Hyderabad Metropolitan Water Supply & Sewerage Board on 18 September 2026 (Notification '
         '04/OG/HM/2026). Applications closed on 17 October 2026. The written exam is tentatively in December 2026; the exact date has not been announced. '
         'Below: the dates, the posts, the pattern and the previous papers.',
    te='TGPSC HMWSSB మేనేజర్ (ఇంజినీరింగ్) నోటిఫికేషన్ 04/OG/HM/2026: 130 పోస్టులు. రాత పరీక్ష డిసెంబర్ 2026లో (తాత్కాలికం).',
    pdf=TG_HM, pdfname='TGPSC Notification No. 04/OG/HM/2026 (Manager (Engineering), HMWSSB), 18 September 2026',
    more_src=[('https://websitenew.tgpsc.gov.in/', 'TGPSC What\'s New (checked 4 November 2026)')],
    related=['tgpsc-amvi-notification.html'],
    sections=[
      ('Important dates', 'table', [
        ('Notification (04/OG/HM/2026)', '18 September 2026'), ('Online applications', '23 September to 17 October 2026, 5 pm (closed; no extension notice)'),
        ('Written examination', 'Tentatively December 2026; exact date to be announced'), ('Hall ticket', 'From 7 days before the exam until 5 pm the day before'),
        ('Mode', 'OMR or computer-based, as TGPSC decides'), ('Exam centres', 'Hyderabad (including HMDA area), Nalgonda, Sangareddy, Mahabubnagar')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Manager (Engineering), HMWSSB, Multi Zone-II'), ('Vacancies', '130 (6 unreserved, 124 local)'),
        ('Branches', '80% Civil, 15% Electrical / Mechanical, 5% CSE / IT / ECE (the notification gives shares, not exact numbers)'),
        ('Pay scale', '₹54,220 – ₹1,33,630'), ('Age', '18 to 44 years on 1 July 2026, plus 5 years for SC, ST, BC and EWS and 10 for PH')]),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I', 'General Studies & General Abilities (English and Telugu)', '150 · 150 · 150 min'),
        ('Paper II', 'The engineering subject concerned (English)', '150 · 300 · 150 min'), ('Total', '', '450')])),
      ('', 'note', 'Selection is on the written marks only; there is no interview. Qualifying marks: 40% OC/EWS/sports, 35% BC, 30% SC/ST/PH. The notification does not mention negative marking. '
                   'Fee: ₹1,000 (OC/BC) or ₹500 (SC/ST/PwD) plus ₹120 exam fee (unemployed exempt).'),
    ],
    faqs=[
      ('Is the HMWSSB Manager exam date out?', 'No. The notification says the exam is tentatively in December 2026; TGPSC had not announced the exact date as of 10 November 2026.'),
      ('Was the HMWSSB Manager last date extended?', 'No extension notice appeared on TGPSC\'s website. Applications closed on 17 October 2026 at 5 pm.'),
      ('When will the HMWSSB Manager hall ticket come?', 'Not yet. As per the notification, hall tickets open 7 days before the exam.'),
      ('Is there negative marking in the HMWSSB Manager exam?', 'The notification does not mention negative marking.'),
      ('How many HMWSSB Manager posts are for Civil?', 'The notification gives shares only: 80% Civil, 15% Electrical/Mechanical, 5% CSE/IT/ECE of the 130 posts.'),
      ('Is Paper 2 out of 150 marks?', 'No. Paper II has 150 questions carrying 300 marks; Paper I is 150 marks; the total is 450.'),
      ('Is there an interview for HMWSSB Manager?', 'No. Selection is on the written exam marks only.'),
      ('What is the HMWSSB Manager salary and age limit?', 'Pay ₹54,220 – ₹1,33,630; age 18 to 44 on 1 July 2026, with relaxations.'),
    ]),
}


ASOF_PAGE = {'upsc-cse-2027-notification.html': '10 November 2026', 'ssc-cgl-2026-notification.html': '10 November 2026',
             'tgpsc-hmwssb-manager-notification-2026.html': '10 November 2026',
             'appsc-eo-grade-3-notification-2026.html': '10 November 2026', 'appsc-fro-notification-2026.html': '10 November 2026',
             'appsc-analyst-grade-2-notification-2026.html': '10 November 2026', 'ap-police-si-notification-2026.html': '10 November 2026',
             'ap-police-constable-notification-2026.html': '10 November 2026', 'ts-police-si-exam-date-hall-ticket-2026.html': '10 November 2026',
             'ts-police-constable-exam-date-hall-ticket-2026.html': '10 November 2026', 'appsc-assistant-environmental-engineer-notification-2026.html': '8 November 2026',
             'appsc-group-1-notification-2026.html': '10 November 2026', 'appsc-group-2-notification-2026.html': '10 November 2026'}   # pages whose answers were written later
# ---------------------------------------------------------------- TGPSC MPSO / ASO (Anil, 8 Nov 2026: link to Notification 07/2026, "pls add pyqs for it in
# telangana section"). The 2018 question booklets were not found online (only TSPSC's final keys), so Anil chose "start with what's available": this page,
# with Paper I practice from TGPSC's General Studies & General Abilities papers already on the site. Add the 2018 papers as an exam when the booklets come.
TG_MPSO = 'https://websitenew.tgpsc.gov.in/preview/RElSRUNUUkVDUlVJVE1FTlROT1RJLzA3LUctMjAyNi1NUFNPLU5PVElGTjIwMjYxMDI4MjI1NDE2LnBkZg==r95v17a0y2d8i13v'
TG_MPSO_2018 = 'https://websitenew.tgpsc.gov.in/preview/RElSRUNUUkVDUlVJVE1FTlROT1RJLzEyMjAxODAyMDYxOC5wZGY=r95v17a0y2d8i13v'
TG_MPSO_KEY1 = 'https://websitenew.tgpsc.gov.in/preview/UFJFU1NOT1RFL2ZpbmFsX0tFWV8xODEyMV9BU08tUEFQRVItSS5wZGY=r95v17a0y2d8i13v'
TG_MPSO_KEY2 = 'https://websitenew.tgpsc.gov.in/preview/UFJFU1NOT1RFL2ZpbmFsX0tFWV8xODEyMl9BU08tUEFQRVItSUkucGRmr95v17a0y2d8i13v'
def _aso_practice():
    """Paper II practice for TGPSC MPSO / ASO: the APPSC Assistant Statistical Officer Paper II papers on the site (added 8 Nov 2026)."""
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'appsc-aso')
    have = [(y, f) for y, f in ((2025, 'appsc-aso-2025-paper2.txt'), (2022, 'appsc-aso-2022-paper2.txt')) if os.path.exists(os.path.join(src, f))]
    if not have:
        return '<p>Paper II (Statistics) previous questions are being added.</p>'
    items = ''.join(f'<li><a href="/appsc-assistant-statistical-officer/papers/appsc-aso-{y}-paper-2-statistics-economics-question-paper-with-answers.html">'
                    f'APPSC Assistant Statistical Officer {y} Paper II: Statistics, Economics, Accountancy &amp; Computers</a></li>' for y, f in have)
    return ('<h2>Practise Paper II with APPSC\'s Statistics papers</h2><p>TSPSC has not put the 2018 question booklets online. The APPSC Assistant Statistical Officer '
            'exam has a Paper II on the same statistics topics (collection of data, central tendency, dispersion and skewness, correlation, time series, index numbers, computers), '
            'with economics and accountancy too. Every question is in English and Telugu with APPSC\'s final key and a short explanation:</p><ul>' + items + '</ul>'
            '<p>All APPSC ASO papers, subject-wise practice and timed tests: <a href="/appsc-assistant-statistical-officer/">APPSC Assistant Statistical Officer previous papers</a>.</p>')


NEW['tgpsc-mpso-aso-notification-2026.html'] = dict(
    exam=None, ename='TGPSC MPSO / ASO', board='TGPSC', site='websitenew.tgpsc.gov.in', crumb='MPSO / ASO Notification 2026', faq_asof='8 November 2026',
    title='TGPSC MPSO / ASO Notification 2026 – 102 Posts, Apply by 27 November, Exam January 2027, Syllabus, Pattern & Previous Papers | Learn with Anil',
    desc='TGPSC Notification 07/G/ES/2026: 102 Mandal Planning and Statistical Officer / Assistant Statistical Officer posts in the Directorate of Economics & '
         'Statistics. Apply online 30 October to 27 November 2026; exam January 2027. Eligibility (degree with Statistics), age 18–44, fee, pay ₹36,750–1,06,990, '
         'zone-wise posts, Paper I General Studies and Paper II Statistics syllabus, and previous papers.',
    h1='TGPSC MPSO / ASO Notification 2026: 102 posts',
    lede='TGPSC Notification 07/G/ES/2026 (28 October 2026) invites online applications for 102 posts of Mandal Planning and Statistical Officer / Assistant '
         'Statistical Officer in the Directorate of Economics & Statistics, Telangana. Apply from 30 October to 27 November 2026, 5 pm; the written exam is '
         'tentatively in January 2027. Below: dates, zone-wise posts, eligibility, the two-paper pattern and syllabus, the 2018 exam, and previous papers to practise.',
    te='టీజీపీఎస్సీ మండల ప్లానింగ్ అండ్ స్టాటిస్టికల్ ఆఫీసర్ / అసిస్టెంట్ స్టాటిస్టికల్ ఆఫీసర్ నోటిఫికేషన్ (నం. 07/2026): 102 పోస్టులు — ఆన్‌లైన్ దరఖాస్తులు '
       'అక్టోబర్ 30 నుంచి నవంబర్ 27, 2026 వరకు. పేపర్-1 జనరల్ స్టడీస్ & జనరల్ ఎబిలిటీస్, పేపర్-2 స్టాటిస్టిక్స్. పరీక్ష జనవరి 2027లో.',
    pdf=TG_MPSO, pdfname='TGPSC Notification No. 07/G/ES/2026 (Mandal Planning and Statistical Officers / Assistant Statistical Officers), 28 October 2026',
    more_src=[(TG_MPSO_2018, 'TSPSC Notification No. 12/2018'), (TG_MPSO_KEY1, 'TSPSC final key, Paper I (18121), 2018'),
              (TG_MPSO_KEY2, 'TSPSC final key, Paper II (18122), 2018')],
    sections=[
      ('Important dates', 'table', [
        ('Notification (07/G/ES/2026)', '28 October 2026'), ('Online applications', '30 October to 27 November 2026, till 5:00 pm'),
        ('Written examination', 'Tentatively January 2027; exact date to be announced'), ('Hall ticket', 'From 7 days before the exam until 5 pm the day before'),
        ('Mode', 'OMR or computer-based (CBRT), as TGPSC decides; scores normalised if held in several sessions'),
        ('Exam centres', 'Hyderabad (including HMDA area), Karimnagar, Khammam, Warangal, Nizamabad'), ('Official website', 'tgpsc.gov.in')]),
      ('Posts, pay and age', 'table', [
        ('Post', 'Mandal Planning and Statistical Officer / Assistant Statistical Officer, Directorate of Economics & Statistics (zonal post)'),
        ('Vacancies', '102 (7 unreserved, 95 local)'), ('Pay scale', '₹36,750 – ₹1,06,990'),
        ('Age', '18 to 44 years on 1 July 2026 (raised from 34 by G.O.Ms.No.86 of 18 May 2026); 5 years more for SC, ST, BC and EWS, 10 for PH, up to 5 for '
                'Telangana government employees')]),
      ('Zone-wise posts', 'table+', (['Zone', 'Districts', 'Posts'], [
        ('I Kaleshwaram', 'Kumrambheem-Asifabad, Mancherial, Peddapalli, Jayashankar-Bhupalapalli, Mulugu', '12'),
        ('II Basara', 'Adilabad, Nirmal, Nizamabad, Jagtial', '14'),
        ('III Rajanna', 'Karimnagar, Rajanna-Sircilla, Siddipet, Medak, Kamareddy', '15'),
        ('IV Bhadradri', 'Bhadradri-Kothagudem, Khammam, Mahabubabad, Hanumakonda, Warangal', '17'),
        ('V Yadadri', 'Suryapet, Nalgonda, Yadadri-Bhuvanagiri, Jangaon', '7'),
        ('VI Charminar', 'Medchal-Malkajgiri, Hyderabad, Ranga Reddy, Sangareddy, Vikarabad', '25'),
        ('VII Jogulamba', 'Mahabubnagar, Narayanpet, Jogulamba-Gadwal, Wanaparthy, Nagarkurnool', '12')])),
      ('', 'note', 'Each zone has 1 unreserved post; the community-wise split is in Annexure-I of the notification.'),
      ('Who can apply', 'list', [
        'A bachelor\'s degree with Statistics as one of the main subjects; or',
        'A bachelor\'s degree with Mathematics, Economics, Commerce or Computer Science as a main subject, with Statistics as a paper in one, two or all three years.',
        'Fee: ₹1,000 application processing fee (₹500 for SC, ST and PwD) plus ₹80 exam fee; unemployed applicants are exempt from the exam fee, employees pay it.']),
      ('Exam pattern', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I', 'General Studies & General Abilities', '150 · 150 · 150 min'),
        ('Paper II', 'Statistics (common for all, degree level)', '150 · 150 · 150 min'), ('Total', '', '300')])),
      ('', 'note', 'Objective type, bilingual (English and Telugu). Selection is on the written marks only; there is no interview. Qualifying marks: 40% OC, EWS and '
                   'sports, 35% BC, 30% SC, ST and PH. The notification does not mention negative marking.'),
      ('Paper I syllabus: General Studies & General Abilities', 'list', [
        'Current affairs (regional, national, international); international relations and events.',
        'General science; India\'s achievements in science and technology; environmental issues and disaster management.',
        'Economy of India and Telangana; geography of India with a focus on Telangana.',
        'Indian Constitution and polity with a focus on local self-government; policies of the Telangana State.',
        'Society, culture, heritage, arts and literature of Telangana; modern Indian history and the national movement; history of Telangana and the statehood movement.',
        'Logical reasoning, analytical ability and data interpretation; basic English.']),
      ('Paper II syllabus: Statistics (degree level)', 'list', [
        'Introduction: meaning and limits of statistics, primary and secondary data, sampling and census, schedules and questionnaires, frequency distributions, tables, diagrams and graphs.',
        'Central tendency, dispersion, skewness and kurtosis: AM, GM, HM, median, mode, deciles, percentiles; range, QD, MD, SD, coefficient of variation; Karl Pearson\'s and Bowley\'s skewness.',
        'Probability: sample space, events, theorems, conditional probability, independence, Bayes\' theorem.',
        'Random variables and distributions: Bernoulli, binomial, Poisson, normal; unbiasedness, consistency, efficiency, sufficiency; large and small sample tests; null and alternative hypotheses.',
        'Correlation and regression: Karl Pearson\'s and Spearman\'s rank correlation, probable error, regression equations and coefficients.',
        'Time series (trend, seasonal variation) and index numbers (price, quantity, tests of adequacy, deflating, cost of living).',
        'Sampling techniques: complete enumeration vs sampling, sample size, simple, stratified and systematic random sampling.',
        'Basics of computers: binary, octal and hexadecimal systems, codes, bits and bytes, memory, logical operators (AND, OR, XOR, NOT, shift), algorithms and flow charts, MS Office.']),
      ('The last MPSO / ASO exam (2018)', 'table', [
        ('Notification', 'TSPSC No. 12/2018, 2 June 2018: 474 posts (pay then ₹24,440 – ₹71,510)'),
        ('Exam', '3 September 2018: Paper I (code 18121) in the forenoon, Paper II Statistics (code 18122) in the afternoon; four booklet series A–D'),
        ('Final keys', 'Released 9 October 2018. Paper I: 3 questions deleted (Series A Q23, Q69, Q86) and two answers accepted for Q70 and Q80. Paper II: '
                       'Series A Q118 deleted; TSPSC later issued a correction to the Paper II final key')]),
      ('', 'html', f'<p>TSPSC\'s official 2018 final keys: <a href="{TG_MPSO_KEY1}" rel="nofollow">Paper I (18121)</a> · '
                   f'<a href="{TG_MPSO_KEY2}" rel="nofollow">Paper II Statistics (18122)</a>.</p>'),
    ],
    faqs=[
      ('What is the last date for TGPSC MPSO / ASO 2026?', '27 November 2026, 5:00 pm. Applications opened on 30 October 2026.'),
      ('How many MPSO / ASO posts are there?', '102 zonal posts: Zone I 12, II 14, III 15, IV 17, V 7, VI 25 and VII 12.'),
      ('When is the TGPSC MPSO / ASO exam?', 'Tentatively in January 2027. TGPSC will announce the exact date; hall tickets come 7 days before.'),
      ('Can B.Sc Maths or B.Com students apply?', 'Yes, if Statistics was a paper in at least one year of the degree. Degrees with Statistics as a main subject, or Maths, '
                                                  'Economics, Commerce or Computer Science with a Statistics paper, qualify.'),
      ('What is the MPSO / ASO age limit?', '18 to 44 years on 1 July 2026, with 5 more years for SC, ST, BC and EWS and 10 for PH.'),
      ('What is the MPSO / ASO salary?', 'Pay scale ₹36,750 – ₹1,06,990.'),
      ('Is there negative marking in MPSO / ASO?', 'The notification does not mention negative marking.'),
      ('Is there an interview?', 'No. Selection is on the 300 marks of the written exam (Paper I and Paper II).'),
      ('When was the last MPSO / ASO exam?', 'On 3 September 2018, under TSPSC Notification 12/2018 for 474 posts.'),
      ('Where can I practise MPSO / ASO Statistics previous questions?', 'TSPSC has not published the 2018 question booklets online. The APPSC Assistant Statistical Officer '
                                                                         'Paper II papers have the same statistics topics (with economics, accountancy and computers), in English and Telugu with APPSC\'s final key: '
                                                                         'see the Paper II practice list on this page.'),
    ],
    tail_html='<h2>Practise Paper I with TGPSC\'s General Studies papers</h2><p>Paper I (General Studies &amp; General Abilities) follows the same syllabus as '
              'the Paper I of other TGPSC posts. These papers have every question with the official key and a short explanation in English and Telugu:</p><ul>'
              '<li><a href="/tgpsc-amvi/papers/tgpsc-amvi-2023-paper-1-general-studies-question-paper-with-answers.html">TGPSC AMVI 2023 Paper I: General Studies &amp; '
              'General Abilities (150 questions)</a></li>'
              '<li><a href="/tgpsc-hmwssb-manager/papers/tgpsc-hmwssb-manager-2015-paper-1-general-studies-question-paper-with-answers.html">TSPSC HMWSSB Manager 2015 '
              'Paper I: General Studies</a></li></ul>'
              + _aso_practice() +
              '<p>More Telangana papers: <a href="/ts-police-pyqs.html">TS Police SI and Constable</a> · '
              '<a href="/exam-notifications.html">all exam notifications</a>.</p>')


def apply(NOTIFS):
    for rel, f in FAQS.items():
        if rel in NOTIFS: NOTIFS[rel]['faqs'] = f; NOTIFS[rel]['faq_asof'] = ASOF_PAGE.get(rel, ASOF)
    for rel, N in NEW.items():
        N.setdefault('faq_asof', ASOF_PAGE.get(rel, ASOF))
        NOTIFS[rel] = N
