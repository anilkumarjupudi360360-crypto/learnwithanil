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
    ('Is the APPSC Group 2 notification 2026 out?', 'Yes. The brief notification No. 37/2026 came on 13 October 2026 (686 posts) and the detailed notification on 10 November 2026, with 720 posts: 471 executive and 249 non-executive.'),
    ('What is the last date for APPSC Group 2 2026?', '11 December 2026, 11:59 pm. Applications opened on 10 November on psc.ap.gov.in; you need your One Time Profile Registration (OTPR) first.'),
    ('Has the APPSC Group 2 last date been extended?', 'The brief notification said 30 November; the detailed notification of 10 November gives 11 December 2026 (11:59 pm) as the last date. No further change as of 11 November 2026.'),
    ('When is the APPSC Group 2 screening test 2026?', 'Sunday 21 February 2027, offline on an OMR sheet. The Mains will be online; APPSC will announce its date separately.'),
    ('How many Deputy Tahsildar posts are there in Group 2 2026?', '203 Deputy Tahsildar posts and 176 Deputy MPDO posts, out of 720 in all.'),
    ('Why did Group 2 posts go up from 686 to 720?', 'Departments reported more vacancies before the detailed notification: 31 Junior Office Assistant posts were added, and a few counts changed (Deputy Tahsildar 200 → 203, Senior Accountant 90 → 91, Junior Accountant 48 → 47).'),
    ('Is the Group 2 exam pattern changed?', 'No. It is still a 150-mark screening test, then two 150-mark Mains papers, then a qualifying Computer Proficiency Test. Selection is on the Mains marks.'),
    ('Is there negative marking in APPSC Group 2?', 'Yes. One-third of a mark is deducted for each wrong answer.'),
    ('What is the APPSC Group 2 fee?', 'Coaching websites quoting the detailed notification give ₹250 application fee + ₹80 exam fee, with the exam fee waived for SC, ST, BC, PwBD, ex-service, white-card and unemployed AP candidates (the same as in 2023). Confirm on psc.ap.gov.in before paying.'),
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
    ('Can I still apply for APPSC Assistant Environmental Engineer?', 'No. APPSC\'s web note of 27 October 2026 extended the last date from 27 October to 9 November 2026 (11:59 pm), and applications closed then. No further extension was reported as of 11 November 2026.'),
    ('Was the APPSC AEE last date extended?', 'Yes, once: from 27 October to 9 November 2026, in the same web note that extended Group-I (Sakshi Education, 29 October; Andhra Jyothy, 28 October).'),
    ('When is the APPSC Assistant Environmental Engineer exam?', 'Not announced as of 11 November 2026. It will be a computer-based test (CBRT); APPSC will publish the date in a web note and the hall ticket.'),
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
    ('Has the AP Police SI 2026 online application started?', 'Not yet, as far as we could find on 11 November 2026. SLPRB says it will announce the application dates in a press note on slprb.ap.gov.in.'),
    ('When is the AP Police SI exam 2026?', 'The Preliminary Written Test date has not been announced yet.'),
    ('How many SI posts are there in AP Police 2026?', '378: 253 SCT SI (Civil), 116 SCT Reserve SI (AR) and 9 SI in the Special Protection Force. SI (Communications) and SI (PTO) have a separate notification.'),
    ('Why do some websites say 2,050 AP Police posts?', 'That counts all six SLPRB notifications of 16 September 2026, not just this one: 378 SI + 60 SI Communications/PTO + 43 Scientific Assistants + 1,156 PC/Firemen/Warders + 200 PC Communications + 213 constable mechanics and drivers (as listed by Adda247 and FreeJobAlert).'),
    ('What is the age limit for AP SI 2026?', '21 to 27 years on 1 July 2026 (born between 2 July 1999 and 1 July 2005), relaxed by up to 5 years for SC, ST, BC and EWS candidates.'),
    ('Is there negative marking in the AP SI prelims?', 'No. No marks are deducted for wrong answers in the AP Police SI written tests.'),
    ('What are the qualifying marks for AP SI?', '40% for OC (and EWS), 35% for BC and 30% for SC and ST, in each paper.'),
  ],
  'ap-police-constable-notification-2026.html': [
    ('Has the AP Police Constable 2026 application started?', 'Not yet, as far as we could find on 11 November 2026. SLPRB will announce the online application dates in a press note on slprb.ap.gov.in.'),
    ('When is the AP Constable exam 2026?', 'The Preliminary Written Test date has not been announced yet.'),
    ('How many AP Police Constable posts are there in 2026?', '1,156 in this notification: 542 SCT PC (Civil), 285 SCT PC (AR), 158 Firemen, 150 Warders (Men) and 21 Warders (Women).'),
    ('What is the age limit for AP Constable 2026?', '18 to 24 years on 1 July 2026 for PC (Civil) and (AR), with the usual relaxations.'),
    ('Is there negative marking in the AP Constable exam?', 'No. No marks are deducted for wrong answers.'),
    ('Do the prelims marks count for selection?', 'No. The Preliminary Written Test is only qualifying (40% OC, 35% BC, 30% SC/ST). Selection is on the Final Written Examination.'),
  ],
  'ts-police-si-exam-date-hall-ticket-2026.html': [
    ('Is the TS Police SI exam postponed?', 'No postponement had been announced as of 11 November 2026. The Preliminary Written Test stays on Sunday, 29 November 2026, forenoon (marked tentative in TGPRB\'s press note of 17 September 2026).'),
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
    ('Is the TS Police Constable exam postponed?', 'No postponement had been announced as of 11 November 2026. The Preliminary Written Test stays on Sunday, 20 December 2026, forenoon (tentative).'),
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
        ('Prelims', '24 May 2026'), ('Qualified for the Mains', '13,343 (result of June 2026)'), ('Mains', 'Began 21 August 2026'), ('Mains result', '5 November 2026: 2,526 candidates qualified for the interview (personality test)'), ('DAF-II (online)', '11 to 25 November 2026, till 6 pm (as reported)'), ('Interviews', 'Schedule not announced as of 11 November 2026')]),
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
      ('Is the UPSC CSE 2027 notification out?', 'No, not as of 11 November 2026. UPSC\'s Calendar 2027 schedules it for 13 January 2027. In 2026 the notification came about three weeks after its calendar date, so a short delay is possible.'),
      ('When is UPSC Prelims 2027?', 'Sunday, 23 May 2027, as per UPSC\'s Calendar 2027.'),
      ('Has the UPSC 2027 exam date changed?', 'No change has been announced as of 11 November 2026. UPSC says calendar dates can change if circumstances require, so check upsc.gov.in.'),
      ('When does UPSC Mains 2027 start?', '20 August 2027, over 5 days.'),
      ('What is the last date to apply for UPSC CSE 2027?', '2 February 2027 as per the calendar; the notification will give the final date.'),
      ('How many vacancies are there in UPSC CSE 2027?', 'Not announced yet; they come with the notification. CSE 2026 had about 933 (CSE 2025: 979).'),
      ('Is the UPSC Mains 2026 result out?', 'Yes. UPSC declared the CSE Mains 2026 result on 5 November 2026: 2,526 candidates qualified for the personality test (interview). Qualified candidates fill the Detailed Application Form (DAF-II) online from 11 to 25 November 2026, till 6 pm (as reported by Indian Masterminds and Dainik Jagran). UPSC will announce the interview schedule and e-summon letters on upsc.gov.in.'),
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
      ('Is the UPSC CAPF 2027 notification out?', 'No, not as of 11 November 2026. It is scheduled for 17 February 2027 in UPSC\'s Calendar 2027.'),
      ('When is the UPSC CAPF AC 2027 exam?', 'Sunday, 4 July 2027.'),
      ('Has the CAPF 2027 exam date changed?', 'No change has been announced as of 11 November 2026. Note it is two weeks earlier than the 2026 exam (19 July 2026).'),
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
      ('Is the EPFO APFC admit card out?', 'Not as of 11 November 2026. UPSC puts the e-admit card on upsc.gov.in a little before the test, usually 1–3 weeks before.'),
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
      ('Is the SSC CGL 2026 Tier 1 result out?', 'Not as of 11 November 2026. It comes after SSC checks the objections; reports expect it in December 2026, but SSC has not given a date.'),
      ('When is SSC CGL Tier 2 2026?', 'SSC has not given an exact date. It is tentatively in December 2026.'),
      ('How many vacancies are there in SSC CGL 2026?', 'About 10,731 (tentative), revised from 12,256 at the notification.'),
      ('Is there negative marking in SSC CGL?', 'Yes. Tier-I: 0.5 mark per wrong answer. Tier-II Paper I: 1 mark per wrong answer (each question carries 3).'),
      ('Do Tier-I marks count in the final merit?', 'No. Tier-I only qualifies you for Tier-II; the final merit is on Tier-II.'),
      ('What is the SSC CGL age limit?', 'It depends on the post: 18–27, 18–30, 20–30 or 18–32 years on 1 August 2026.'),
      ('When will the SSC CGL 2027 notification come?', 'Not announced. It will appear in SSC\'s 2027-28 exam calendar, which is not out yet.'),
    ]),
  'rrb-ntpc-2026-notification.html': dict(
    exam='rrb-ntpc', board='RRB', site='rrbapply.gov.in and the regional RRB websites', crumb='RRB NTPC 2026 Notification',
    title='RRB NTPC 2026 Notification (CEN 06/2026 & 07/2026): 5,236 Posts, Applications Closed, Exam Date, Age, Fee, Pattern & Previous Papers | Learn with Anil',
    desc='RRB NTPC 2026: CEN 06/2026 (Graduate, 3,548 posts) and CEN 07/2026 (Undergraduate, 1,688 posts). Application dates (closed), correction window, exam date status, '
         'age limit, fee, post-wise vacancies and pay, CBT-1 and CBT-2 pattern, and RRB NTPC previous year papers with RRB\'s answer key.',
    h1='RRB NTPC 2026: 5,236 posts, applications closed, CBT date awaited',
    lede='The Railway Recruitment Boards notified 5,236 NTPC posts in 2026: 3,548 for graduates (CEN 06/2026) and 1,688 for Class 12 pass candidates (CEN 07/2026). '
         'Both application windows have closed; the correction windows run in November 2026 and the CBT-1 date is still to be announced. Below: dates, posts, eligibility, pattern and the NTPC previous papers.',
    hi='RRB NTPC 2026: स्नातक (CEN 06/2026) के 3,548 और 12वीं स्तर (CEN 07/2026) के 1,688 पद। आवेदन बंद; CBT-1 की तिथि अभी घोषित नहीं।',
    pdf='https://www.rrbapply.gov.in/', pdfname='RRB application portal, rrbapply.gov.in (CEN 06/2026 and CEN 07/2026 are also on every regional RRB website)',
    more_src=[('https://www.pw.live/railway/exams/rrb-ntpc-2026-notification', 'Physics Wallah: post-wise vacancies, dates, fee and pay of CEN 06/2026 and 07/2026'),
              ('https://www.careerindia.com/news/rrb-ntpc-2026-recruitment-apply-online-ug-graduate-posts-dates-eligibility-011-67119.html', 'CareerIndia: dates, correction windows and age limits'),
              ('https://www.manabadi.co.in/ManabadiV2/updates/206600/rrb-ntpc-graduate-recruitment-2026-last-date-extension-notice', 'Manabadi: graduate last date extended to 8 November 2026'),
              ('https://rrbsecunderabad.gov.in/advertisement_category/cen-no-06-2025-ntpc-graduate/', 'RRB Secunderabad: CEN 06/2025 notices (CBT-1 key 6 April 2026, CBT-2 held 10 July 2026)')],
    sections=[
      ('Where RRB NTPC 2026 stands', 'table', [
        ('Notifications', 'CEN 06/2026 (Graduate) and CEN 07/2026 (Undergraduate, Class 12 level)'),
        ('Graduate applications', '8 October to 6 November 2026, reported extended to 8 November 2026 (closed); correction window 9–18 November 2026'),
        ('Undergraduate applications', '15 October to 13 November 2026 (closed); fee till 15 November; correction window 16–25 November 2026'),
        ('CBT-1', 'Not announced by RRB yet. One report puts the graduate CBT-1 in the fourth week of December 2026; treat it as unconfirmed'),
        ('Admit card', 'City slip about 10 days and e-call letter about 4 days before your exam date (as in earlier cycles)'),
        ('Vacancies', '5,236 in all: 3,548 graduate + 1,688 undergraduate (tentative; the early indicative notice said 3,477 graduate)')]),
      ('Posts and pay', 'table+', (['Post', 'Level', 'Vacancies', 'Starting basic pay'], [
        ('Goods Train Manager', 'Graduate', '2,750', '₹29,200 (Level 5)'),
        ('Chief Commercial cum Ticket Supervisor', 'Graduate', '127', '₹35,400 (Level 6)'),
        ('Junior Accounts Assistant cum Typist', 'Graduate', '300', '₹29,200 (Level 5)'),
        ('Senior Clerk cum Typist', 'Graduate', '371', '₹29,200 (Level 5)'),
        ('Commercial cum Ticket Clerk', 'Undergraduate', '700', '₹21,700 (Level 3)'),
        ('Accounts Clerk cum Typist', 'Undergraduate', '200', '₹19,900 (Level 2)'),
        ('Junior Clerk cum Typist', 'Undergraduate', '600', '₹19,900 (Level 2)'),
        ('Trains Clerk', 'Undergraduate', '188', '₹19,900 (Level 2)')])),
      ('Exam pattern', 'table+', (['Stage', 'Subjects', 'Questions / time', 'Negative marking'], [
        ('CBT-1 (screening)', 'General Awareness 40, Mathematics 30, General Intelligence & Reasoning 30', '100 questions, 100 marks, 90 minutes', '1/3 mark per wrong answer'),
        ('CBT-2 (merit)', 'General Awareness 50, Mathematics 35, General Intelligence & Reasoning 35', '120 questions, 120 marks, 90 minutes', '1/3 mark per wrong answer'),
        ('After CBT-2', 'Document verification and medical examination; for typist posts the typing test is done after joining (as reported)', '', '')])),
      ('Who could apply', 'list', [
        'Graduate posts: a degree; age 18–33 years on 1 January 2027. Undergraduate posts: Class 12 (10+2); age 18–30 years on 1 January 2027.',
        'Age relaxation as in earlier cycles: OBC (NCL) 3 years, SC/ST 5 years, PwBD 10 years and more, ex-servicemen by service.',
        'Fee ₹500 (₹400 refunded after you sit CBT-1); SC, ST, ex-servicemen, PwBD, women, transgender, minority and EBC candidates pay ₹250 (fully refunded after CBT-1).']),
      ('The previous cycle (CEN 06/2025 and 07/2025)', 'list', [
        'Graduate (5,810 posts): CBT-1 held 16–27 March 2026, answer key 6 April 2026, CBT-1 result 12 June 2026, CBT-2 held 10 July 2026 (answer key 15 July 2026).',
        'Undergraduate (3,058 posts): CBT-1 held on 7–9 May and 13–21 June 2026; answer key and response sheets 27 June 2026.',
        'The 2024 cycle (CEN 05/2024 and 06/2024): graduate CBT-1 5–24 June 2025 and CBT-2 13 October 2025; undergraduate CBT-1 7 August – 8 September 2025.']),
    ],
    faqs=[
      ('Is the RRB NTPC 2026 last date extended?', 'For graduates (CEN 06/2026), the last date of 6 November 2026 was reported extended to 8 November 2026. The undergraduate window (CEN 07/2026) closed on 13 November 2026. Both are closed now; only the correction windows remain (graduate 9–18 November, undergraduate 16–25 November 2026).'),
      ('When is the RRB NTPC 2026 exam date?', 'RRB has not announced the CBT-1 dates as of 15 November 2026. One report says the graduate CBT-1 is tentatively in the fourth week of December 2026, but RRB has not confirmed it. The exam city slip comes about 10 days before the exam.'),
      ('How many vacancies are there in RRB NTPC 2026?', '5,236: 3,548 graduate-level posts (CEN 06/2026) and 1,688 undergraduate posts (CEN 07/2026). Goods Train Manager has the most, 2,750.'),
      ('What is the RRB NTPC age limit for 2026?', '18–33 years for graduate posts and 18–30 years for undergraduate posts, on 1 January 2027, with the usual relaxations (OBC 3, SC/ST 5 years).'),
      ('Is there negative marking in RRB NTPC?', 'Yes. One-third of a mark is cut for every wrong answer in both CBT-1 and CBT-2. Unanswered questions get zero.'),
      ('Do CBT-1 marks count in the final merit?', 'No. CBT-1 only shortlists candidates for CBT-2; the merit list is drawn from CBT-2 marks (and the typing or aptitude test where a post needs it).'),
      ('Can a Class 12 pass candidate apply for graduate posts?', 'No. Graduate posts (CEN 06/2026) need a degree. Class 12 pass candidates apply under CEN 07/2026 for Commercial cum Ticket Clerk, Accounts Clerk cum Typist, Junior Clerk cum Typist and Trains Clerk.'),
      ('Where can I practise RRB NTPC previous year papers?', 'On learnwithanil.in/rrb-ntpc/: real RRB NTPC CBT-1 and CBT-2 shift papers from 2025 and 2026 with RRB\'s answer key and explanations, in English and Hindi, as timed tests or subject-wise.'),
    ]),
  # Anil, 15 Nov 2026 ("SSC MTS...add pyqs and other required details like other sites"). Checked 15 Nov 2026: no MTS 2026 notice on SSC's site as reported
  # by vocab24 (13 Nov) and mockli (6 Nov); MTS 2025 dates from Careers360, Shiksha and Free Press Journal.
  'ssc-mts-2026-notification.html': dict(
    exam='ssc-mts', board='SSC', site='ssc.gov.in', crumb='SSC MTS 2026 Status',
    title='SSC MTS 2026 Notification: Not Out Yet (Postponed from 30 June), Eligibility, Age, Exam Pattern, MTS 2025 Result & Previous Papers | Learn with Anil',
    desc='SSC MTS & Havaldar 2026: the notice due on 30 June 2026 was postponed and is not out as of 15 November 2026. Eligibility (Class 10), age 18–25 / 18–27, '
         'fee ₹100, the 90-question CBE pattern, where MTS 2025 stands, and SSC MTS previous year papers with answers in English and Hindi.',
    h1='SSC MTS 2026 notification: not out yet',
    lede='SSC\'s exam calendar for 2026-27 listed the Multi-Tasking (Non-Technical) Staff and Havaldar (CBIC & CBN) Examination 2026 notice for 30 June 2026. '
         'It was postponed, and SSC had not published it as of 15 November 2026. The last cycle, MTS 2025, was notified on 26 June 2025 and its computer-based exam '
         'was held in February 2026. Below: where things stand, the rules of the last notice (they rarely change), the exam pattern and the MTS previous papers.',
    hi='एसएससी एमटीएस 2026: 30 जून 2026 को आने वाला नोटिस स्थगित हुआ और 15 नवंबर 2026 तक जारी नहीं हुआ है। पात्रता: 10वीं पास; आयु 18–25 / 18–27 वर्ष।',
    pdf='https://ssc.gov.in/', pdfname='Staff Selection Commission notices, ssc.gov.in (MTS and Havaldar Examination 2025 notice of 26 June 2025; the MTS 2026 notice is awaited)',
    more_src=[('https://vocab24.com/ssc-mts/2026', 'Vocab24, 13 November 2026: MTS 2026 notice not published yet'),
              ('https://news.careers360.com/ssc-mts-notification-2025-registration-begins-multi-tasking-staff-havaldar-recruitment-vacancy-age-limit-salary-syllabus-cut-off/amp', 'Careers360: MTS 2025 notice, age, fee and pattern'),
              ('https://competition.careers360.com/exams/ssc-mts', 'Careers360: MTS 2025 exam held 4–20 February 2026, answer key 3 March 2026'),
              ('https://www.freepressjournal.in/education/ssc-mts-havaldar-result-2026-out-at-sscgovin-8274-shortlisted-for-petpst-727-candidates-flagged-for-malpractice', 'Free Press Journal, 4 August 2026: MTS 2025 CBE result for the Havaldar PET/PST')],
    sections=[
      ('Where SSC MTS 2026 stands', 'table', [
        ('Notice (SSC calendar date)', '30 June 2026 — postponed'), ('Notice published?', 'No, as of 15 November 2026'),
        ('Applications', 'Will open with the notice, online at ssc.gov.in (about four weeks in past cycles)'),
        ('Computer-based exam', 'Date to be announced with the notice'), ('Vacancies', 'Will be given in the notice (MTS 2025: 7,948 after revision)')]),
      ('Where MTS 2025 stands (the last cycle)', 'table', [
        ('Notice', '26 June 2025; applications 26 June to 24 July 2025'), ('Computer-based exam', '4 to about 20 February 2026 (rescheduled at some centres)'),
        ('Answer key', '3 March 2026 (as reported)'), ('CBE result', '3 August 2026: list for the Havaldar PET/PST; a further list on 7 October 2026 (as reported)'),
        ('Havaldar PET/PST', '24 to 31 August 2026'), ('Final result (MTS and Havaldar)', 'Reports differ; check ssc.gov.in')]),
      ('Exam pattern (last notice)', 'table+', (['Session', 'Subjects (questions)', 'Marks · time · negative marking'], [
        ('Session I', 'Numerical & Mathematical Ability (20), Reasoning Ability & Problem Solving (20)', '120 marks · 45 minutes · no negative marking'),
        ('Session II', 'General Awareness (25), English Language & Comprehension (25)', '150 marks · 45 minutes · 1 mark cut per wrong answer'),
        ('Havaldar only', 'Physical Efficiency Test and Physical Standard Test', 'qualifying')])),
      ('Who could apply (last notice)', 'list', [
        'Class 10 (matriculation) or equivalent, passed on or before the cut-off date in the notice.',
        'Age on 1 August of the notice year: 18–25 years for MTS, 18–27 years for Havaldar (CBIC & CBN) and some MTS posts; relaxation OBC 3, SC/ST 5, PwBD 10 years.',
        'Fee ₹100; women, SC, ST, PwBD and ex-servicemen pay nothing.',
        'The paper is set in English, Hindi and 13 regional languages; you choose the language when you apply.']),
    ],
    faqs=[
      ('Is the SSC MTS 2026 notification out?', 'No, not as of 15 November 2026. SSC\'s calendar had it on 30 June 2026, but it was postponed and SSC has not given a new date.'),
      ('When will the SSC MTS 2026 notification come?', 'SSC has not announced a date. Coaching sites have guessed several months (October, November); none of these is an SSC date. Watch ssc.gov.in.'),
      ('What is the SSC MTS age limit?', 'In the last notice: 18–25 years for MTS and 18–27 years for Havaldar and some MTS posts, on 1 August of the notice year, with the usual relaxations (OBC 3, SC/ST 5, PwBD 10 years).'),
      ('What qualification do I need for SSC MTS?', 'Class 10 (matriculation) or equivalent from a recognised board.'),
      ('Is there negative marking in SSC MTS?', 'Only in Session II (General Awareness and English): 1 mark is cut for each wrong answer. Session I (Maths and Reasoning) has no negative marking. Every question carries 3 marks.'),
      ('Is the SSC MTS 2025 result out?', 'The computer-based exam result for the Havaldar PET/PST came on 3 August 2026, and the PET/PST was held from 24 to 31 August 2026. Check ssc.gov.in for the final result of MTS and Havaldar.'),
      ('Where can I practise SSC MTS previous papers?', 'On the SSC MTS page of this site: whole shifts of MTS 2024 with SSC\'s answer key and an explanation for every question, in English and Hindi, as timed mock tests or by subject.'),
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
      ('Is the TGPSC AMVI notification 2026 out?', 'No. TGPSC\'s list of 2026 notifications (checked 11 November 2026) has no AMVI post.'),
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
      ('Is the HMWSSB Manager exam date out?', 'No. The notification says the exam is tentatively in December 2026; TGPSC had not announced the exact date as of 11 November 2026 (it is not in TGPSC\'s exam schedule web note of 28 September either).'),
      ('Was the HMWSSB Manager last date extended?', 'No extension notice appeared on TGPSC\'s website. Applications closed on 17 October 2026 at 5 pm.'),
      ('When will the HMWSSB Manager hall ticket come?', 'Not yet. As per the notification, hall tickets open 7 days before the exam.'),
      ('Is there negative marking in the HMWSSB Manager exam?', 'The notification does not mention negative marking.'),
      ('How many HMWSSB Manager posts are for Civil?', 'The notification gives shares only: 80% Civil, 15% Electrical/Mechanical, 5% CSE/IT/ECE of the 130 posts.'),
      ('Is Paper 2 out of 150 marks?', 'No. Paper II has 150 questions carrying 300 marks; Paper I is 150 marks; the total is 450.'),
      ('Is there an interview for HMWSSB Manager?', 'No. Selection is on the written exam marks only.'),
      ('What is the HMWSSB Manager salary and age limit?', 'Pay ₹54,220 – ₹1,33,630; age 18 to 44 on 1 July 2026, with relaxations.'),
    ]),
}


ASOF_PAGE = {'ssc-mts-2026-notification.html': '15 November 2026', 'rrb-ntpc-2026-notification.html': '15 November 2026', 'upsc-cse-2027-notification.html': '11 November 2026', 'ssc-cgl-2026-notification.html': '11 November 2026', 'tgpsc-hmwssb-manager-notification-2026.html': '11 November 2026', 'appsc-eo-grade-3-notification-2026.html': '11 November 2026', 'appsc-fro-notification-2026.html': '11 November 2026', 'appsc-analyst-grade-2-notification-2026.html': '11 November 2026', 'ap-police-si-notification-2026.html': '11 November 2026', 'ap-police-constable-notification-2026.html': '11 November 2026', 'ts-police-si-exam-date-hall-ticket-2026.html': '11 November 2026', 'ts-police-constable-exam-date-hall-ticket-2026.html': '11 November 2026', 'appsc-assistant-environmental-engineer-notification-2026.html': '11 November 2026', 'appsc-group-1-notification-2026.html': '11 November 2026', 'appsc-group-2-notification-2026.html': '11 November 2026', 'upsc-capf-2027-notification.html': '11 November 2026', 'upsc-epfo-apfc-2026-notification.html': '11 November 2026', 'tgpsc-amvi-notification.html': '11 November 2026', 'appsc-amvi-notification-2026.html': '11 November 2026', 'ts-police-si-answer-key-2026.html': '11 November 2026', 'ts-police-constable-answer-key-2026.html': '11 November 2026', 'tgpsc-mpso-aso-notification-2026.html': '11 November 2026'}   # pages whose answers were re-checked later (scheduled checks, 11 Nov 2026)
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
    exam=None, ename='TGPSC MPSO / ASO', board='TGPSC', site='websitenew.tgpsc.gov.in', crumb='MPSO / ASO Notification 2026', faq_asof='11 November 2026',
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


# ---------------------------------------------------------------- RPF SI and Constable (Anil, 15 Nov 2026: "RPF SI + Constable...add the pyqs and
# required details like other exams"). No 2026 notification exists: these are status pages (the next cycle moves to SSC) with the facts of the last
# RRB recruitment (CEN RPF 01/2024 and 02/2024). Sources checked 15 Nov 2026: RRB notices (RRB Bhopal SI notice and CBT cut-off PDFs, RRB Chandigarh
# CEN RPF 02/2024 notices page), the G.S.R. 766(E) text as reproduced by StaffNews, and exam-news sites for dates RRB pages no longer list.
RPF_SI_NOTICE = 'https://rrbbhopal.gov.in/notice%20Sub%20Inspector%20RPF%2001-2024_English.pdf'
RPF_SI_CUTOFF = 'https://rrbbhopal.gov.in/2025/RPF_01-2024_SI_CBT_CUT-OFF.pdf'
RPF_PC_PAGE = 'https://rrbcdg.gov.in/2024-02-rpf.php'
RPF_RULES = 'https://www.staffnews.in/2025/10/railway-protection-force-amendment-rules-2025.html'
RPF_ASOF = '15 November 2026'
_RPF_PATTERN = ('Exam pattern of the last RPF CBT (RRB)', 'table+', (['Section', 'Questions', 'Marks'], [
    ('General Awareness', '50', '50'), ('Arithmetic', '35', '35'), ('General Intelligence & Reasoning', '35', '35'), ('Total (90 minutes)', '120', '120')]))
_RPF_SSC = ('What changes with the SSC', 'list', [
    'The Railway Protection Force (Amendment) Rules, 2025 (G.S.R. 766(E), 17 October 2025) say direct recruitment of Sub-Inspectors and Constables (Executive) will follow the Staff Selection Commission\'s recruitment procedure for the Central Armed Police Forces (CAPFs). Earlier the Railway Recruitment Boards (RRBs) held it.',
    'Constable (Executive): above 18 and below 23 years on the date of the notification, and a pass in the High School (10th) examination or equivalent (new rule 48.3).',
    'Physical standards for the executive cadre: height 170 cm, chest 80 cm unexpanded and 85 cm expanded; women and reserved categories as per the CAPF standards. The medical examination is done by CAPF medical officers or government doctors.',
    'The SSC has not yet issued an RPF notification or announced the new exam pattern (as of 15 November 2026). Until it does, the RRB papers below are the best guide to the level and the topics.'])
NEW['rpf-si-notification-2026.html'] = dict(
    exam='rpf-si', board='RPF', site='ssc.gov.in and rpf.indianrailways.gov.in', crumb='RPF SI 2026: notification status', faq_asof=RPF_ASOF,
    title='RPF SI Notification 2026 – Status (SSC to Conduct), Last Exam CEN RPF 01/2024, Age, Pattern & Previous Papers | Learn with Anil',
    desc='RPF Sub-Inspector recruitment 2026: no notification yet; from the next cycle the SSC conducts it (RPF Amendment Rules, 17 October 2025). Facts of the '
         'last exam (CEN RPF 01/2024: 452 posts, CBT 2–13 December 2024, final result 26 August 2025), eligibility, the 120-question pattern, and shift-wise previous papers with answers.',
    h1='RPF SI 2026: next recruitment through the SSC',
    lede='There is no RPF Sub-Inspector notification for 2026 yet. From the next cycle the Staff Selection Commission (SSC), not the Railway Recruitment Boards, '
         'conducts the recruitment, under the Railway Protection Force (Amendment) Rules, 2025. Below: the status, what changes, the facts of the last RRB exam '
         '(CEN RPF 01/2024), its pattern, and its question papers with answers.',
    hi='आरपीएफ एसआई भर्ती 2026: अगली भर्ती कर्मचारी चयन आयोग (SSC) करेगा; 15 नवंबर 2026 तक अधिसूचना जारी नहीं हुई। पिछली परीक्षा (CEN RPF 01/2024) के शिफ्ट-वार प्रश्न पत्र उत्तर सहित।',
    pdf=RPF_SI_NOTICE, pdfname='RRB notice CEN RPF 01/2024 (Sub-Inspector, Executive)',
    more_src=[(RPF_SI_CUTOFF, 'RRB, CBT cut-off for SI (3 March 2025)'), (RPF_RULES, 'Railway Protection Force (Amendment) Rules, 2025, G.S.R. 766(E) (text as reproduced by StaffNews)')],
    related=['rpf-constable-notification-2026.html'],
    sections=[
      ('Status (as of 15 November 2026)', 'table', [
        ('RPF SI 2026 notification', 'Not issued yet'), ('Who will conduct it', 'Staff Selection Commission (SSC), from the next cycle'),
        ('Rule change', 'RPF (Amendment) Rules, 2025, G.S.R. 766(E) of 17 October 2025'),
        ('Where to watch', 'ssc.gov.in and rpf.indianrailways.gov.in'), ('Last RPF SI exam', 'CEN RPF 01/2024 (RRB), CBT in December 2024')]),
      ('', 'note', 'Vacancy numbers and dates for RPF 2026 seen on some websites are not official. Wait for the SSC notice.'),
      _RPF_SSC,
      ('The last RPF SI recruitment: CEN RPF 01/2024 (RRB)', 'table', [
        ('Notification', '14 April 2024; online applications 15 April to 14 May 2024'),
        ('Posts', '452 Sub-Inspectors (Executive) in the RPF and RPSF'), ('Pay', 'Level 6 of the 7th CPC, initial pay ₹35,400'),
        ('Age', '20 to 28 years on 1 July 2024, with the usual relaxations'), ('Qualification', 'A bachelor\'s degree from a recognised university'),
        ('Computer-based test', '2, 3, 9, 12 and 13 December 2024, three shifts a day'),
        ('Answer key and question papers', '17 December 2024; objections until 22 December 2024'),
        ('CBT result', '3 March 2025 (normalised cut-off marks out of 100)'), ('PET, PMT and document verification', '22 June to 2 July 2025'),
        ('Final result', '26 August 2025')]),
      _RPF_PATTERN,
      ('', 'note', 'One mark a question; one-third of a mark is cut for a wrong answer. The SI paper is set at graduation level. Candidates who qualify in the CBT take the Physical Efficiency Test (PET) and Physical Measurement Test (PMT), and the merit list follows the CBT marks.'),
    ],
    faqs=[
      ('Is the RPF SI 2026 notification out?', 'No, not as of 15 November 2026. From the next cycle the SSC conducts RPF recruitment; neither the SSC nor the RPF has issued a notice yet.'),
      ('Who will conduct the next RPF SI exam?', 'The Staff Selection Commission (SSC). The RPF (Amendment) Rules, 2025, notified on 17 October 2025, say selection of Sub-Inspectors and Constables (Executive) follows the SSC\'s procedure for the Central Armed Police Forces.'),
      ('Will the RPF SI exam pattern change?', 'Probably, because the SSC will follow its CAPF procedure, but the SSC has not published the new scheme yet. The last RPF SI exam (RRB) had 120 questions in 90 minutes: General Awareness 50, Arithmetic 35 and Reasoning 35.'),
      ('How many posts were there in the last RPF SI recruitment?', '452 Sub-Inspector (Executive) posts under CEN RPF 01/2024. The final result came on 26 August 2025.'),
      ('What was the RPF SI age limit?', '20 to 28 years on 1 July 2024 under CEN RPF 01/2024, with the usual relaxations for reserved categories. The next notice will give the new dates.'),
      ('What is the RPF SI salary?', 'Pay Level 6 of the 7th Pay Commission, initial basic pay ₹35,400 a month, plus allowances.'),
      ('Is there negative marking in RPF SI?', 'Yes. In the RRB CBT one-third of a mark was cut for each wrong answer.'),
      ('Where can I practise RPF SI previous papers?', 'On this site: whole shift papers of the RPF SI CBT of December 2024 in English and Hindi, with RRB\'s answer key, explanations and a 90-minute timer.'),
    ])
NEW['rpf-constable-notification-2026.html'] = dict(
    exam='rpf-constable', board='RPF', site='ssc.gov.in and rpf.indianrailways.gov.in', crumb='RPF Constable 2026: notification status', faq_asof=RPF_ASOF,
    title='RPF Constable Notification 2026 – Status (SSC to Conduct), New Age Limit 18–23, Last Exam CEN RPF 02/2024 & Previous Papers | Learn with Anil',
    desc='RPF Constable recruitment 2026: no notification yet; from the next cycle the SSC conducts it, and the new rules set the age at 18–23 years. Facts of the '
         'last exam (CEN RPF 02/2024: 4,208 posts, CBT 2–18 March 2025, 42,143 qualified for PET), the 120-question pattern, and shift-wise previous papers with answers.',
    h1='RPF Constable 2026: next recruitment through the SSC',
    lede='There is no RPF Constable notification for 2026 yet. From the next cycle the Staff Selection Commission (SSC), not the Railway Recruitment Boards, conducts '
         'the recruitment, and the Railway Protection Force (Amendment) Rules, 2025 set a new age limit of 18 to 23 years. Below: the status, what changes, the facts of '
         'the last RRB exam (CEN RPF 02/2024), its pattern, and its question papers with answers.',
    hi='आरपीएफ कांस्टेबल भर्ती 2026: अगली भर्ती कर्मचारी चयन आयोग (SSC) करेगा; नई आयु सीमा 18 से 23 वर्ष; 15 नवंबर 2026 तक अधिसूचना जारी नहीं हुई। पिछली परीक्षा (CEN RPF 02/2024) के शिफ्ट-वार प्रश्न पत्र उत्तर सहित।',
    pdf=RPF_PC_PAGE, pdfname='RRB Chandigarh, all notices of CEN RPF 02/2024 (Constable)',
    more_src=[(RPF_RULES, 'Railway Protection Force (Amendment) Rules, 2025, G.S.R. 766(E) (text as reproduced by StaffNews)')],
    related=['rpf-si-notification-2026.html'],
    sections=[
      ('Status (as of 15 November 2026)', 'table', [
        ('RPF Constable 2026 notification', 'Not issued yet'), ('Who will conduct it', 'Staff Selection Commission (SSC), from the next cycle'),
        ('New age limit', 'Above 18 and below 23 years on the date of the notification (RPF Amendment Rules, 2025)'),
        ('Where to watch', 'ssc.gov.in and rpf.indianrailways.gov.in'), ('Last RPF Constable exam', 'CEN RPF 02/2024 (RRB), CBT in March 2025')]),
      ('', 'note', 'Vacancy numbers and dates for RPF 2026 seen on some websites are not official. Wait for the SSC notice.'),
      _RPF_SSC,
      ('The last RPF Constable recruitment: CEN RPF 02/2024 (RRB)', 'table', [
        ('Notification', '14 April 2024; online applications 15 April to 14 May 2024'),
        ('Posts', '4,208 Constables (Executive) in the RPF and RPSF'), ('Pay', 'Level 3 of the 7th CPC, initial pay ₹21,700'),
        ('Age', '18 to 28 years on 1 July 2024 (the new rules lower it to 18–23 for the next cycle)'), ('Qualification', '10th (matriculation) pass or equivalent'),
        ('Computer-based test', '2 to 18 March 2025, three shifts a day'),
        ('Question papers, responses and answer key', '24 to 29 March 2025 (objections in the same window)'),
        ('CBT result', '19 June 2025: 42,143 candidates shortlisted for PET, PMT and document verification'),
        ('PET, PMT and document verification', '13 November to 6 December 2025'),
        ('Final panel', '16 February 2026; zone allotment and medical examination notice 23 February 2026')]),
      _RPF_PATTERN,
      ('', 'note', 'One mark a question; one-third of a mark is cut for a wrong answer. The Constable paper is set at 10th-class level. Candidates who qualify in the CBT take the Physical Efficiency Test (PET) and Physical Measurement Test (PMT), and the merit list follows the CBT marks.'),
    ],
    faqs=[
      ('Is the RPF Constable 2026 notification out?', 'No, not as of 15 November 2026. From the next cycle the SSC conducts RPF recruitment; neither the SSC nor the RPF has issued a notice yet. Vacancy figures circulating online are unofficial.'),
      ('Who will conduct the next RPF Constable exam?', 'The Staff Selection Commission (SSC). The RPF (Amendment) Rules, 2025, notified on 17 October 2025, say selection of Constables and Sub-Inspectors (Executive) follows the SSC\'s procedure for the Central Armed Police Forces.'),
      ('What is the new RPF Constable age limit?', 'Above 18 and below 23 years on the date of the notification, under the RPF (Amendment) Rules, 2025, with relaxations as per government rules. In the last recruitment (CEN RPF 02/2024) it was 18 to 28 years on 1 July 2024.'),
      ('What is the qualification for RPF Constable?', 'A pass in the 10th (High School) examination or equivalent from a recognised board.'),
      ('How many posts were there in the last RPF Constable recruitment?', '4,208 Constable (Executive) posts under CEN RPF 02/2024. The CBT result of 19 June 2025 shortlisted 42,143 candidates for the physical tests, and the final panel came on 16 February 2026.'),
      ('What is the RPF Constable salary?', 'Pay Level 3 of the 7th Pay Commission, initial basic pay ₹21,700 a month, plus allowances.'),
      ('Is there negative marking in RPF Constable?', 'Yes. In the RRB CBT one-third of a mark was cut for each wrong answer.'),
      ('Where can I practise RPF Constable previous papers?', 'On this site: whole shift papers of the RPF Constable CBT of March 2025 in English and Hindi, with RRB\'s answer key, explanations and a 90-minute timer.'),
    ])
# ---------------------------------------------------------------- RRB Group D (Anil, 15 Nov 2026: "RRB Group D...add pyqs and other details like other exams").
# CEN 09/2025 result came on 12 Nov 2026, so the page leads with the result (what students search this week), then the notification facts.
# Sources: news/coaching sites quoting the RRB notices (RRB websites were not readable from here); two sources for every date and number used.
NEW['rrb-group-d-result-2026.html'] = dict(
    exam='rrb-group-d', board='RRB', site='rrb.indianrailways.gov.in and your regional RRB website', crumb='RRB Group D 2026: Result, Notification',
    faq_asof='15 November 2026',
    title='RRB Group D Result 2026 Out (12 November) – CEN 09/2025 Scorecard from 16 November, PET, Cut Off, 22,195 Posts, Pattern & Previous Papers | Learn with Anil',
    desc='RRB Group D 2026 (CEN 09/2025, 22,195 Level-1 posts): CBT held 3–25 August 2026, answer key 7 September, result declared 12 November 2026 zone-wise '
         'with PET shortlists and cut-offs, scorecards from 16 November. Eligibility, fee, pattern, PET standards, and RRB Group D previous papers with answers.',
    h1='RRB Group D 2026: result out, PET next',
    lede='The Railway Recruitment Boards declared the RRB Group D (CEN 09/2025) CBT result on 12 November 2026: each RRB published a PDF of roll numbers '
         'shortlisted for the Physical Efficiency Test (PET) with zone-wise and category-wise cut-off marks. Scorecards open from 16 November 2026. '
         'Below: where things stand as of 15 November 2026, the notification facts, the exam pattern, PET standards and the previous papers to practise.',
    hi='आरआरबी ग्रुप डी 2026 (CEN 09/2025): सीबीटी का परिणाम 12 नवंबर 2026 को घोषित — पीईटी के लिए चयनित रोल नंबर और कट-ऑफ क्षेत्रवार; स्कोरकार्ड 16 नवंबर से।',
    pdf='https://rrb.indianrailways.gov.in/', pdfname='Railway Recruitment Boards (CEN 09/2025 notices on each regional RRB website, e.g. rrbsecunderabad.gov.in)',
    more_src=[('https://testbook.com/news/railway-rrb-group-d-result-2026-date/', 'Testbook, 14 November 2026: result 12 November, scorecards 16 November'),
              ('https://www.oliveboard.in/rrb-group-d-result/', 'Oliveboard: result 12 November 2026 for 22,195 vacancies'),
              ('https://prepp.in/rrb-group-d-exam/results', 'Prepp, 14 November 2026: zone-wise PET shortlists'),
              ('https://www.freejobalert.com/articles/rrb-group-d-cen-09-2025-result-2026-3068505', 'FreeJobAlert: CBT result 12 November 2026'),
              ('https://www.pw.live/news/rrb-group-d-exam-date-2026-cen-09-2025-cbt-1-schedule-revised', 'PW: revised CBT schedule, 3–25 August 2026'),
              ('https://news.careers360.com/rrb-group-d-answer-key-2026-out-cbt-objections-last-date-september-17-response-sheet-pdf-link/amp', 'Careers360: answer key and objections')],
    sections=[
      ('Where RRB Group D 2026 stands', 'table', [
        ('Notification', 'CEN 09/2025, detailed notice 30 January 2026 (short notice December 2025)'),
        ('Vacancies', '22,195 Level-1 posts across the railway zones'),
        ('Applications', '31 January to 9 March 2026 (extended from 2 March); closed'),
        ('CBT', '3–6, 9–14, 17–21 and 25 August 2026 (over)'),
        ('Answer key', 'Provisional key with response sheets released 7 September 2026; objection window closed in mid-September'),
        ('Result', 'Declared 12 November 2026: PET shortlist and cut-offs, zone-wise, on each RRB website'),
        ('Scorecard', 'From 16 November 2026 (5 pm) on the RRB websites, with your registration number and date of birth'),
        ('Next stage', 'Physical Efficiency Test (PET), conducted zone-wise by the RRCs; dates are announced by each RRC'),
        ('RRB Secunderabad (Telangana, Andhra Pradesh)', '1,705 candidates shortlisted for PET against 1,012 vacancies (as reported by Testbook and qmaths)')]),
      ('Who could apply', 'list', [
        'Class 10 pass, or ITI, or the National Apprenticeship Certificate (NAC) granted by NCVT (post-wise details in the notification).',
        'Age 18 to 33 years on 1 January 2026; relaxation OBC-NCL 3 years, SC/ST 5 years, more for PwBD and ex-servicemen.',
        'Fee ₹500 (₹400 refunded after the candidate takes the CBT). SC, ST, ex-servicemen, PwBD, women, transgender, minorities and Economically Backward Class paid a fee of ₹250, refunded in full after the CBT.',
        'Pay: Level 1 of the 7th CPC Pay Matrix, starting basic pay ₹18,000 a month plus allowances.']),
      ('Exam pattern (CBT)', 'table+', (['Section', 'Questions'], [
        ('General Science', '25'), ('Mathematics', '25'), ('General Intelligence & Reasoning', '30'), ('General Awareness & Current Affairs', '20'),
        ('Total', '100 questions, 100 marks, 90 minutes (120 for eligible PwBD with a scribe); one-third mark cut for a wrong answer')])),
      ('Physical Efficiency Test (PET)', 'table+', (['', 'Men', 'Women'], [
        ('Lift and carry', '35 kg for 100 metres in 2 minutes, in one chance, without putting it down', '20 kg for 100 metres in 2 minutes, in one chance, without putting it down'),
        ('Run', '1,000 metres in 4 minutes 15 seconds, in one chance', '1,000 metres in 5 minutes 40 seconds, in one chance')])),
      ('The previous cycle (CEN 08/2024)', 'list', [
        '32,438 Level-1 posts; CBT from 27 November 2025, with the last shifts in January and February 2026.',
        'Result declared 1 July 2026; PET in July and August 2026.',
        'The papers on this website are from this cycle: RRB\'s own question papers with its answer key, shift by shift, in English and Hindi.']),
    ],
    faqs=[
      ('Is the RRB Group D result 2026 out?', 'Yes. The RRBs declared the CEN 09/2025 CBT result on 12 November 2026 as zone-wise PDFs of roll numbers shortlisted for the PET, with category-wise cut-off marks. Check your own RRB\'s website.'),
      ('When will the RRB Group D scorecard 2026 come?', 'From 16 November 2026 (5 pm) on the RRB websites. Log in with your registration number and date of birth to see your raw and normalised marks.'),
      ('When is the RRB Group D PET 2026?', 'Each zone\'s Railway Recruitment Cell (RRC) announces its own PET dates and issues PET admit cards. As of 15 November 2026 the dates were not out for all zones.'),
      ('How many candidates qualified for PET in RRB Secunderabad?', '1,705 roll numbers were shortlisted for PET against 1,012 vacancies of RRB Secunderabad (as reported by Testbook and qmaths). Check the official PDF on rrbsecunderabad.gov.in.'),
      ('What is the RRB Group D cut off 2026?', 'Cut-offs are given zone-wise and category-wise in normalised marks in each RRB\'s result PDF. They differ from zone to zone, so compare your normalised score with your own RRB\'s cut-off.'),
      ('How many posts are there in RRB Group D 2026?', '22,195 Level-1 posts (CEN 09/2025): Track Maintainer Grade-IV, Pointsman-B, Assistants in various departments and other posts.'),
      ('Is there negative marking in RRB Group D?', 'Yes. One-third of a mark is cut for each wrong answer. Each question carries 1 mark.'),
      ('When will the next RRB Group D notification come?', 'Not announced as of 15 November 2026. The last two notices were CEN 08/2024 (32,438 posts) and CEN 09/2025 (22,195 posts).'),
    ])
# ---------------------------------------------------------------- SSC GD Constable (Anil, 15 Nov 2026: "SSC GD Constable...add pyqs and other details like
# other exams"). Facts as of 15 November 2026; result and PET/PST facts from news and coaching sites that quote SSC's notices (SSC's own site blocks fetches).
NEW['ssc-gd-constable-2027-notification.html'] = dict(
    exam='ssc-gd', board='SSC', site='ssc.gov.in', crumb='SSC GD 2027 Notification', faq_asof='15 November 2026',
    title='SSC GD Constable 2027 Notification: Expected Date, Exam Jan–Mar 2027, GD 2026 Result & PET/PST, Pattern & Previous Papers | Learn with Anil',
    desc='SSC GD Constable 2027: the notification listed in SSC\'s calendar for 30 September 2026 is not out yet (15 November 2026); exam tentatively January–March 2027. '
         'GD 2026 result (12 October 2026, 1,97,408 shortlisted), PET/PST, pattern, eligibility, salary and SSC GD previous year papers with answers.',
    h1='SSC GD Constable 2027 notification: when it comes, and where GD 2026 stands',
    lede='SSC\'s exam calendar listed the Constable (GD) 2027 notification for 30 September 2026, with the computer-based exam in January–March 2027. '
         'As of 15 November 2026 it has not been issued. The 2026 recruitment (25,487 posts) is at the physical-test stage: the CBE result came on 12 October 2026. '
         'Below: the status of both, the exam pattern, who can apply and the SSC GD previous papers to practise.',
    hi='एसएससी जीडी कांस्टेबल 2027: नोटिफिकेशन (कैलेंडर में 30 सितंबर 2026) अभी जारी नहीं हुआ है; परीक्षा जनवरी–मार्च 2027 (संभावित)। जीडी 2026 का परिणाम 12 अक्टूबर 2026 को आया।',
    pdf='https://ssc.gov.in/', pdfname='Staff Selection Commission notices, ssc.gov.in (exam calendar 2026-27; Constable (GD) 2026 notice of 1 December 2025 and result notice of 12 October 2026)',
    more_src=[('https://www.indiajobalerts.com/?p=12521', 'India Job Alerts, quoting SSC\'s result notice of 12 October 2026'),
              ('https://www.careerpower.in/blog/ssc-gd-constable-result-and-cut-off-2026-out', 'Career Power, GD 2026 result numbers'),
              ('https://news.kollegeapply.com/news/ssc-gd-physical-exam-date-2026', 'KollegeApply, 11 November 2026: PET/PST from 26 November (tentative)'),
              ('https://www.pw.live/ssc/exams/ssc-gd-2027-form-kab-aayega', 'Physics Wallah: GD 2027 notification delayed beyond 30 September')],
    sections=[
      ('SSC GD 2027: where it stands', 'table', [
        ('Notification', 'Listed in SSC\'s calendar for 30 September 2026; not issued as of 15 November 2026'),
        ('Computer-based exam', 'January–March 2027 (tentative, as per the calendar)'),
        ('Vacancies', 'Will come with the notification (2026 had 25,487)'), ('Official website', 'ssc.gov.in')]),
      ('SSC GD 2026: where it stands', 'table', [
        ('Notification', '1 December 2025; applications 1–31 December 2025'), ('Vacancies', '25,487'),
        ('Computer-based exam', '27 April to 30 May 2026 (over)'),
        ('CBE result', '12 October 2026: 1,97,408 of 21,56,776 who appeared shortlisted for PET/PST (1,81,251 men, 15,782 women, 375 more men for the SSF); re-issued with category corrections on 23 October'),
        ('Final answer key and marks', 'Out in November 2026 on ssc.gov.in; reports say they can be downloaded till 17 November'),
        ('PET / PST', 'Conducted by the CAPFs with the CRPF as the nodal force; reported from 26 November to about 11 December 2026 (tentative). Call letters on rect.crpf.gov.in')]),
      ('Exam pattern (computer-based exam)', 'table+', (['Part', 'Subject', 'Questions · marks'], [
        ('A', 'General Intelligence & Reasoning', '20 · 40'), ('B', 'General Knowledge & General Awareness', '20 · 40'),
        ('C', 'Elementary Mathematics', '20 · 40'), ('D', 'English or Hindi', '20 · 40'), ('Total', '60 minutes', '80 · 160')])),
      ('', 'note', '0.25 mark is cut for each wrong answer. The paper is set in English, Hindi and 13 regional languages (Telugu included). Those who qualify go on to the '
                   'Physical Efficiency Test and Physical Standard Test, then a detailed medical examination and document verification.'),
      ('Who can apply (as in the 2026 notification)', 'list', [
        'Class 10 (matriculation) pass from a recognised board.',
        'Age 18 to 23 years on the cut-off date (1 January 2026 for GD 2026); 3 years more for OBC and 5 for SC and ST.',
        'Posts: Constable (GD) in the BSF, CISF, CRPF, ITBP, SSB and SSF, Rifleman (GD) in the Assam Rifles, Sepoy in the NCB. Pay Level 3: ₹21,700 – ₹69,100.',
        'Fee ₹100; women, SC, ST and ex-servicemen pay nothing.']),
    ],
    faqs=[
      ('Is the SSC GD 2027 notification out?', 'Not as of 15 November 2026. SSC\'s calendar listed it for 30 September 2026; coaching sites now expect it later in 2026.'),
      ('When is the SSC GD 2027 exam?', 'Tentatively January to March 2027, as per SSC\'s calendar. The exact dates will come after the notification.'),
      ('Is the SSC GD 2026 result out?', 'Yes. SSC declared the computer-based exam result on 12 October 2026, shortlisting 1,97,408 candidates for the PET/PST.'),
      ('When is the SSC GD 2026 PET/PST?', 'News reports give 26 November to about 11 December 2026 (tentative). The CRPF issues the call letters on rect.crpf.gov.in; go by the date on yours.'),
      ('Is there negative marking in SSC GD?', 'Yes. 0.25 mark is cut for each wrong answer; a right answer earns 2 marks.'),
      ('What is the SSC GD age limit?', '18 to 23 years on the cut-off date, with 3 more years for OBC and 5 for SC and ST.'),
      ('What is the SSC GD Constable salary?', 'Pay Level 3: ₹21,700 – ₹69,100 a month in basic pay, plus allowances.'),
      ('Where can I practise SSC GD previous papers?', 'On Learn with Anil: SSC GD Constable 2025 shift papers with SSC\'s answers and explanations, as 60-minute timed tests or subject-wise practice.'),
    ])
ASOF_PAGE['ssc-gd-constable-2027-notification.html'] = '15 November 2026'

NEW['tnpsc-group-4-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: TNPSC Group 4 (exam 10 January 2027); facts from TNPSC's own PDFs read on 15 Nov 2026
    exam='tnpsc-group-4', board='TNPSC', site='tnpsc.gov.in', crumb='TNPSC Group 4 Notification 2026', faq_asof='15 November 2026',
    title='TNPSC Group 4 Notification 2026 (No. 11/2026): 6,574 Posts, Exam on 10 January 2027, Age Limit Raised, Pattern & Previous Papers | Learn with Anil',
    desc='TNPSC Group 4 (CCSE-IV) 2026: Notification No. 11/2026 of 6 October 2026, 6,574 vacancies (VAO 291, Junior Assistant, Typist, Steno-Typist and more), '
         'applications closed 8 November 2026 (extended from 5 November), written exam on 10 January 2027. Age limit raised by five years, exam pattern, fee and '
         'TNPSC Group 4 previous year papers with answers in Tamil and English.',
    h1='TNPSC Group 4 notification 2026: 6,574 posts, exam on 10 January 2027',
    lede='TNPSC issued Notification No. 11/2026 for the Combined Civil Services Examination-IV (Group-IV Services) on 6 October 2026: 6,574 vacancies, '
         'including 291 Village Administrative Officers. Applications closed on 8 November 2026 after an extension, and the written exam is on Sunday, 10 January 2027. '
         'Below: the key dates, the posts, who can apply, the exam pattern and the TNPSC Group 4 previous papers to practise.',
    ta='டிஎன்பிஎஸ்சி குரூப் 4 (ஒருங்கிணைந்த குடிமைப் பணிகள் தேர்வு–IV) அறிவிக்கை எண் 11/2026: 6,574 பணியிடங்கள்; எழுத்துத் தேர்வு 10.01.2027; '
       'விண்ணப்பிக்க கடைசி நாள் 08.11.2026 வரை நீட்டிக்கப்பட்டது; வயது உச்ச வரம்பு ஐந்து ஆண்டுகள் உயர்த்தப்பட்டது.',
    pdf='https://www.tnpsc.gov.in/Document/english/group_english.pdf', pdfname='TNPSC Notification No. 11/2026 (Advertisement No. 747), 6 October 2026, tnpsc.gov.in',
    more_src=[('https://www.tnpsc.gov.in/Document/english/Addendum%20%2011B.pdf', 'TNPSC Addendum 11B/2026 (4 November 2026): last date extended to 8 November 2026'),
              ('https://www.tnpsc.gov.in/Document/english/Amendment%20to%20the%20notification.pdf', 'TNPSC amendment to para 4.1 (age limit), 4 November 2026, G.O.(Ms) No.68 of 30 October 2026'),
              ('https://www.tnpsc.gov.in/Document/english/Group%20IV%20Addendum%2011A_English.pdf', 'TNPSC Addendum 11A/2026 (29 October 2026)'),
              ('https://www.tnpsc.gov.in/english/press_releases.aspx', 'TNPSC press release 127/2026 (4 November 2026)')],
    sections=[
      ('Key dates', 'table', [
        ('Notification', 'No. 11/2026, dated 6 October 2026 (Advertisement No. 747)'),
        ('Online application', '6 October to 8 November 2026, 11.59 pm (extended from 5 November by Addendum 11B/2026); apply at tnpscexams.in after One Time Registration'),
        ('Written exam', 'Sunday, 10 January 2027, 9.30 am to 12.30 pm (OMR)'),
        ('Hall ticket', 'On tnpscexams.in before the exam (TNPSC announces the date in a press release); it is not sent by post'),
        ('Official website', 'tnpsc.gov.in and tnpscexams.in')]),
      ('Posts and vacancies (6,574)', 'table+', (['Post', 'Vacancies'], [
        ('Village Administrative Officer (VAO)', '291'),
        ('Junior Assistant (all departments and boards, including Junior Assistant (Accounts) 422 and Junior Assistant cum Typist 6)', '3,743'),
        ('Typist', '1,572'),
        ('Steno-Typist (Grade III) 376, Personal Clerk 60, Shorthand Typist 28', '464'),
        ('Revenue Assistant 96, Tax Collector 107, Bill Collector 97, Junior Administrative Assistant 55', '355'),
        ('Executive Officer Grade IV (HR&CE) 46, Junior Inspector of Co-operative Societies 8, Record Clerk 19, Laboratory Assistant 23, Senior Laboratory Assistant 1, '
         'Sales Assistant 10, Telephone Operator 1', '108'),
        ('Forest Watcher 40, Forest Guard with Driving Licence 1', '41'),
        ('Total', '6,574')])),
      ('', 'note', 'Vacancy figures are from TNPSC\'s notification table (6 October 2026). TNPSC often adds posts through addenda before counselling; check tnpsc.gov.in for the latest list.'),
      ('Exam pattern (single paper, SSLC standard)', 'table+', (['Part', 'Subject', 'Questions · marks'], [
        ('A', 'Tamil Eligibility-cum-Scoring Test (in Tamil only)', '100 · 150'),
        ('B', 'General Studies (Tamil and English)', '75 · 150 (with Part C)'),
        ('C', 'Aptitude and Mental Ability (Tamil and English)', '25'),
        ('Total', '3 hours, OMR, objective', '200 · 300')])),
      ('', 'note', 'Parts B and C are valued only if the candidate scores at least 40% (60 marks) in Part A; the marks of all three parts together decide the rank. '
                   'The minimum qualifying mark is 90 out of 300 for all communities. There is no interview. Each question has a fifth option, (E) "Answer not known"; '
                   'leaving a question blank costs 0.5 mark. Differently abled candidates who studied only English may take General English (SSLC standard) instead of Part A.'),
      ('Who can apply', 'list', [
        'Minimum qualification: a pass in SSLC (10th standard); Typist, Steno-Typist and some other posts also need the technical qualifications listed in the notification.',
        'Age as on 1 July 2026 (as amended on 4 November 2026 under G.O.(Ms) No.68 of 30 October 2026, which raised the upper limit by five years): for most posts 18 to 35 years '
        'for "Others", 37 for BC(OBCM), BCM and MBC/DC, and 40 for SC, SC(A) and ST; VAO from 21. For many posts there is no upper limit for BC, MBC, SC and ST candidates '
        'who hold a qualification higher than the minimum. See the amendment for each post and the concessions for persons with benchmark disability, ex-servicemen and destitute widows.',
        'Fee: TNPSC One Time Registration fee of Rs. 150 (valid five years) and an exam fee of Rs. 100, unless exempted (see the notification for the categories).']),
    ],
    faqs=[
      ('When is the TNPSC Group 4 exam 2027?', 'Sunday, 10 January 2027, from 9.30 am to 12.30 pm, as fixed in Notification No. 11/2026.'),
      ('Was the TNPSC Group 4 last date extended?', 'Yes. Addendum 11B/2026 of 4 November 2026 extended the last date from 5 November to 8 November 2026, 11.59 pm, after the age limit was raised. Applications are now closed.'),
      ('How many vacancies are there in TNPSC Group 4 2026?', '6,574 in Notification No. 11/2026, including 291 VAO posts, about 3,743 Junior Assistant posts and 1,572 Typist posts.'),
      ('Was the TNPSC Group 4 age limit increased?', 'Yes. G.O.(Ms) No.68 of 30 October 2026 raised the upper age limit by five years for all categories, and TNPSC amended the notification on 4 November 2026 (for most posts: 35 for "Others", 37 for BC/BCM/MBC, 40 for SC/ST, as on 1 July 2026).'),
      ('What is the TNPSC Group 4 exam pattern?', 'One OMR paper of 200 questions for 300 marks in 3 hours: Part A Tamil (100 questions, 150 marks, at least 40% needed), Part B General Studies (75) and Part C Aptitude & Mental Ability (25) for 150 marks. No interview.'),
      ('What is the minimum qualifying mark for TNPSC Group 4?', '90 out of 300 for all communities, and at least 60 of 150 in Part A Tamil.'),
      ('When will the TNPSC Group 4 hall ticket be released?', 'Not announced as of 15 November 2026. TNPSC releases it on tnpscexams.in before the exam and announces it in a press release; it is not sent by post.'),
      ('Where can I practise TNPSC Group 4 previous papers?', 'On Learn with Anil: the TNPSC Group 4 papers of 2025, 2024 and 2022, Part A Tamil and Part B GS & Aptitude, with TNPSC\'s final answers and explanations in Tamil and English, as 3-hour timed tests or subject-wise practice.'),
    ])
ASOF_PAGE['tnpsc-group-4-notification-2026.html'] = '15 November 2026'


NEW['kea-fda-sda-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: Karnataka FDA/SDA (exams 8-17 January 2027); facts from KEA's own notification PDFs (in Kannada), read on 16 Nov 2026
    exam='karnataka-fda-sda', board='KEA', site='cetonline.karnataka.gov.in/kea', crumb='KEA FDA SDA Notification 2026', faq_asof='16 November 2026',
    title='KEA FDA SDA Notification 2026: 5,431 Group-C Posts in Karnataka, Apply by 25 November, Exams 9–17 January 2027, Pattern & Previous Papers | Learn with Anil',
    desc='KEA FDA and SDA recruitment 2026: four Karnataka Examinations Authority notifications of 29 October 2026 for 5,431 Group-C posts (FDA level 2,163 + 563, '
         'SDA level 2,070 + 635), online applications till 25 November 2026, Kannada language test 8 January and papers 9, 10, 16 and 17 January 2027. '
         'Age limit, fee, exam pattern and KEA FDA/SDA previous year papers with answers in Kannada and English.',
    h1='KEA FDA and SDA notification 2026: 5,431 posts, exams in January 2027',
    lede='The Karnataka Examinations Authority (KEA) issued four notifications on 29 October 2026 to fill 5,431 Group-C posts in Karnataka government departments, '
         'boards and corporations: First Division Assistant (FDA) and equivalent posts for graduates, and Second Division Assistant (SDA) and equivalent posts for II PUC '
         'holders, each for the rest of Karnataka (RPC) and for Kalyana Karnataka (KK). Applications are open till 25 November 2026. '
         'Below: the key dates, the posts, who can apply, the exam pattern and the KEA FDA/SDA previous papers to practise.',
    kn='ಕರ್ನಾಟಕ ಪರೀಕ್ಷಾ ಪ್ರಾಧಿಕಾರ (ಕೆಇಎ): ವಿವಿಧ ಇಲಾಖೆಗಳ ಗ್ರೂಪ್-ಸಿ ಎಫ್‌ಡಿಎ, ಎಸ್‌ಡಿಎ ಮತ್ತು ಸಮಾನ ಹುದ್ದೆಗಳ ನೇಮಕಾತಿ 2026 — 5,431 ಹುದ್ದೆಗಳು; '
       'ಆನ್‌ಲೈನ್ ಅರ್ಜಿಗೆ ಕೊನೆಯ ದಿನಾಂಕ 25.11.2026; ಕನ್ನಡ ಭಾಷಾ ಪರೀಕ್ಷೆ 08.01.2027; ಸ್ಪರ್ಧಾತ್ಮಕ ಪರೀಕ್ಷೆ 09, 10, 16, 17 ಜನವರಿ 2027.',
    pdf='https://cetonline.karnataka.gov.in/kea/gpcfdasdarpc2026', pdfname='KEA notifications ED/KEA/14 and 16/Recruitment/2026 (RPC), 29 October 2026, cetonline.karnataka.gov.in/kea',
    more_src=[('https://cetonline.karnataka.gov.in/kea/gpcfdasdakk2026', 'KEA notifications ED/KEA/15 and 17/Recruitment/2026 (Kalyana Karnataka), 29 October 2026'),
              ('https://cetonline.karnataka.gov.in/kearecruitment2026app/login', 'KEA online application (Group-C 2026)')],
    sections=[
      ('Key dates', 'table', [
        ('Notifications', 'ED/KEA/14, 15, 16 and 17/Recruitment/2026, all dated 29 October 2026'),
        ('Online application', '30 October to 25 November 2026 on cetonline.karnataka.gov.in/kea; fee by 26 November 2026'),
        ('Kannada language test', 'Friday, 8 January 2027, 3.00 to 5.00 pm (only for candidates who are not exempt)'),
        ('FDA-level papers', 'Kalyana Karnataka: Saturday, 9 January 2027 · Rest of Karnataka: Sunday, 10 January 2027'),
        ('SDA-level papers', 'Kalyana Karnataka: Saturday, 16 January 2027 · Rest of Karnataka: Sunday, 17 January 2027'),
        ('Timings', 'Paper-1 10.30 am to 12.30 pm; Paper-2 2.30 to 4.30 pm (offline, OMR)'),
        ('Admit card', 'To be downloaded from the KEA website; KEA will announce the date')]),
      ('Posts and vacancies (5,431)', 'table+', (['Notification', 'Level (qualification)', 'Posts'], [
        ('No. 14 (RPC)', 'FDA and equivalent (degree)', '2,163'),
        ('No. 15 (Kalyana Karnataka)', 'FDA and equivalent (degree)', '563'),
        ('No. 16 (RPC)', 'SDA and equivalent (II PUC)', '2,070'),
        ('No. 17 (Kalyana Karnataka)', 'SDA and equivalent (II PUC)', '635'),
        ('Total', '', '5,431')])),
      ('', 'note', 'Largest posts in No. 14 (RPC, FDA level): Accounts Assistant, Audit and Accounts Department 490; Warden (Men), Social Welfare 294; FDA, Judiciary 249; '
                   'Hostel Superintendent (Men), Backward Classes Welfare 180; Gram Panchayat Secretary & Rural Development Assistant Grade-1 135; FDA in Zilla and Taluk Panchayats 100; '
                   'Commercial Tax Inspector 48. Largest posts in No. 16 (RPC, SDA level): SDA, Judiciary 522; SDA, Commercial Taxes 500; Gram Panchayat Secretary & Rural Development '
                   'Assistant Grade-2 284; SDA in Zilla and Taluk Panchayats 200; Junior Accounts Assistant 130. KEA says the post-wise figures are provisional.'),
      ('Exam pattern', 'table+', (['Paper', 'Subjects', 'Questions · marks · time'], [
        ('Paper-1', 'General Knowledge: current events, general science, geography, Indian and Karnataka history, Indian Constitution and public administration, '
                    'Karnataka economy, rural development and Panchayat Raj, land reforms and social change in Karnataka, IT in governance, environment, mental ability', '100 · 100 · 2 hours'),
        ('Paper-2', 'General Kannada, General English, Computer Knowledge', '100 · 100 · 2 hours'),
        ('Kannada language test', 'Qualifying only (SSLC first-language Kannada standard); at least 50 of 150 marks', '150 marks')])),
      ('', 'note', 'Objective (OMR) questions with four options. A quarter mark is deducted for each wrong answer; a question left blank also loses a quarter mark unless its fifth '
                   '("not attempted") circle is shaded, for which five extra minutes are given. A candidate must score at least 35% in the competitive exam. Selection is on the total '
                   'marks of the competitive exam, by merit and reservation, through KEA\'s online counselling (options) and document verification. Candidates who studied Kannada as a '
                   'first or second language at SSLC or above, studied in Kannada medium, or passed the compulsory Kannada test earlier are exempt from the Kannada language test.'),
      ('Who can apply', 'list', [
        'FDA level (Nos. 14 and 15): a degree; some posts need a specific degree (Accounts Assistant: B.Com, BBM or BBA; Warden and Hostel Superintendent: degree with B.Ed; '
        'Commercial Tax Inspector: degree with Economics or Mathematics, or B.Com). SDA level (Nos. 16 and 17): II PUC or an equivalent; a few posts need Commerce or a computer course.',
        'Age as on 25 November 2026: at least 18; at most 40 years for General Merit, 43 for Categories 2A, 2B, 3A and 3B, and 45 for SC, ST and Category-1. These limits already '
        'include the one-time five-year relaxation of the Government order of 29 January 2026. Persons with disabilities, widows and Karnataka government employees get further relaxation.',
        'Fee (online only, not refundable): Rs. 750 for General Merit and Categories 2A, 2B, 3A, 3B; Rs. 500 for SC, ST, Category-1, ex-servicemen and transgender candidates; '
        'Rs. 250 for persons with disabilities.']),
    ],
    faqs=[
      ('What is the last date to apply for KEA FDA SDA 2026?', '25 November 2026 on cetonline.karnataka.gov.in/kea; the fee can be paid till 26 November 2026.'),
      ('When is the KEA FDA SDA exam 2027?', 'The Kannada language test is on 8 January 2027. FDA-level papers: 9 January (Kalyana Karnataka) and 10 January 2027 (rest of Karnataka). SDA-level papers: 16 January (Kalyana Karnataka) and 17 January 2027 (rest of Karnataka). Paper-1 is from 10.30 am and Paper-2 from 2.30 pm.'),
      ('How many vacancies are there in KEA FDA SDA 2026?', '5,431 in four notifications: 2,163 FDA-level and 2,070 SDA-level posts for the rest of Karnataka, and 563 FDA-level and 635 SDA-level posts for Kalyana Karnataka.'),
      ('Is the KEA FDA SDA exam conducted by KPSC?', 'No. These 2026 Group-C posts are being filled by the Karnataka Examinations Authority (KEA), which also conducted the Group-C exams of its 2025 recruitment.'),
      ('What is the KEA FDA SDA exam pattern?', 'Two OMR papers of 100 questions and 100 marks each, 2 hours each: Paper-1 General Knowledge and Paper-2 General Kannada, General English and Computer Knowledge, with a quarter mark deducted for each wrong answer. At least 35% is needed.'),
      ('What is the age limit for KEA FDA SDA 2026?', '18 to 40 years for General Merit, 43 for 2A/2B/3A/3B and 45 for SC/ST/Category-1, as on 25 November 2026 (including the one-time five-year relaxation).'),
      ('What is the KEA FDA SDA application fee?', 'Rs. 750 for General Merit and 2A/2B/3A/3B, Rs. 500 for SC/ST/Category-1, ex-servicemen and transgender candidates, and Rs. 250 for persons with disabilities.'),
      ('Where can I practise KEA FDA SDA previous papers?', 'On Learn with Anil: KEA\'s 2026 FDA-level, SDA-level and Kalyana Karnataka Group-C papers, Paper-1 General Knowledge and Paper-2 Kannada, English & Computer Knowledge, with KEA\'s revised key and explanations in Kannada and English, as 2-hour timed tests or subject-wise practice.'),
    ])
ASOF_PAGE['kea-fda-sda-notification-2026.html'] = '16 November 2026'


NEW['karnataka-teacher-recruitment-notification-2026.html'] = dict(   # Anil, 16 Nov 2026: Karnataka Teacher Recruitment (GPSTR); facts from the department's candidate guidelines of 17 Aug 2026 (in Kannada) and news of the date extensions, read on 16 Nov 2026
    exam='karnataka-gpstr', board='the School Education Department, Karnataka', site='schooleducation.karnataka.gov.in', crumb='Karnataka Teacher Recruitment 2026', faq_asof='16 November 2026',
    title='Karnataka Teacher Recruitment 2026: 15,000 Posts (GPT 9,000, AM 4,950, PST 1,050), Exam Pattern, Last Date & GPSTR Previous Papers | Learn with Anil',
    desc='Karnataka teacher recruitment 2026 (GPSTR): 15,000 posts in government primary and high schools, Graduate Primary Teacher and Computer Science Teacher 9,000, '
         'Assistant Master and PE Grade-1 4,950, Primary School Teacher and PE Grade-2 1,050. Online applications till 16 November 2026, exam pattern (two 100-mark papers, '
         '35% in each), merit weightage and GPSTR previous year papers with answers in Kannada and English.',
    h1='Karnataka teacher recruitment 2026: 15,000 posts, exam date awaited',
    lede='The School Education Department of Karnataka is filling 15,000 teacher posts in government primary and high schools for 2026-27: Graduate Primary Teachers (GPT) '
         'and Computer Science Teachers for classes 6–8, Assistant Masters and PE teachers for high schools, and Primary School Teachers for classes 1–5. Its Centralised '
         'Admission Cell (K.G. Road, Bengaluru) conducts the competitive exam. Below: the dates, the posts, the exam pattern and the GPSTR previous papers to practise.',
    kn='ಶಾಲಾ ಶಿಕ್ಷಣ ಇಲಾಖೆ: ಸರ್ಕಾರಿ ಪ್ರಾಥಮಿಕ ಮತ್ತು ಪ್ರೌಢ ಶಾಲೆಗಳಲ್ಲಿ 15,000 ಶಿಕ್ಷಕರ ಹುದ್ದೆಗಳ ನೇಮಕಾತಿ 2026 (ಜಿಪಿಟಿ/ಸಿಎಸ್‌ಟಿ 9,000; ಪ್ರೌಢ ಶಾಲಾ ಸಹಶಿಕ್ಷಕರು/ದೈ.ಶಿ.ಶಿ ಗ್ರೇಡ್-1 4,950; '
       'ಪ್ರಾಥಮಿಕ ಶಾಲಾ ಶಿಕ್ಷಕರು/ದೈ.ಶಿ.ಶಿ ಗ್ರೇಡ್-2 1,050). ಪತ್ರಿಕೆ-1 ಮತ್ತು ಪತ್ರಿಕೆ-2 ಕಡ್ಡಾಯ, ಪ್ರತಿ ಪತ್ರಿಕೆಯಲ್ಲಿ ಕನಿಷ್ಠ ಶೇ.35 ಅಂಕಗಳು.',
    pdf='https://schooleducation.karnataka.gov.in/uploads/media_to_upload1786967745.pdf',
    pdfname='Candidate guidelines No. DPI-CPIOCAC(ODEX)/1/2026, 17 August 2026, Centralised Admission Cell, School Education Department (in Kannada)',
    more_src=[('https://schooleducation.karnataka.gov.in/cacell/en', 'Online application: Recruitment of Teachers 2026 (Centralised Admission Cell)')],
    sections=[
      ('Key dates', 'table', [
        ('Government notification', 'No. EP 80 DPB 2026, 10 August 2026 (district-wise notifications by the appointing authorities)'),
        ('Candidate guidelines', 'No. DPI-CPIOCAC(ODEX)/1/2026, 17 August 2026'),
        ('Online application', 'Opened 18 August 2026; the last date (first 7 September) was extended several times, finally to 16 November 2026. Corrections till 18 November; fee till 28 November 2026 (as reported)'),
        ('Exam date', 'Not announced as of 16 November 2026. The August guidelines had a timetable for 5–22 October 2026, which was dropped when the application dates were extended'),
        ('Admit card', 'On the department website about 10 days before the exam')]),
      ('Posts (15,000)', 'table+', (['Cadre', 'Classes', 'Posts'], [
        ('Graduate Primary Teacher (GPT) and Computer Science Teacher (CST)', '6–8 (CST 1–8)', '9,000'),
        ('Assistant Master (high school) and PE Teacher Grade-1', '8–10', '4,950'),
        ('Primary School Teacher (PST) and PE Teacher Grade-2', '1–5 (PE 1–8)', '1,050'),
        ('Total', '', '15,000')])),
      ('', 'note', 'GPT/CST posts by subject: Maths & Science 3,109; Kannada 2,557; Social Science 1,415; Biological Science 776; English 643; Computer Science 500 '
                   '(5,472 in the rest of Karnataka and 3,528 in Kalyana Karnataka). One online application covers every post a candidate is eligible for.'),
      ('Exam pattern', 'table+', (['Paper', 'What it covers', 'Questions · marks · time'], [
        ('Paper-1 General', 'Common general paper for each cadre group (PST & PE Grade-2; GPT & CST; AM & PE Grade-1)', '100 · 100 · 2 hours'),
        ('Paper-2 Subject', 'PST: Mathematics, EVS & Social Science; PE: Physical Education; GPT: the subject applied for (Maths & Science, Biological Science, Social Science, '
                            'Kannada, English); CST: Computer Science; AM: Science, Arts, Kannada or English', '100 · 100 · 2 hours')])),
      ('', 'note', 'Objective multiple-choice questions on OMR sheets, printed in Kannada and English. Both papers are compulsory, and a candidate must score at least 35% in each '
                   'paper to be considered. Merit (2026 rules): the exam carries 70% weightage, the TET score 20% and academic and teacher-education marks the rest.'),
    ],
    faqs=[
      ('What is the last date to apply for Karnataka teacher recruitment 2026?', '16 November 2026, after several extensions (first 7 September). Corrections are allowed till 18 November and the fee till 28 November 2026, as reported.'),
      ('When is the Karnataka GPSTR exam 2026?', 'Not announced as of 16 November 2026. The department\'s August guidelines listed exams from 5 to 22 October 2026, but that timetable was dropped when the application dates were extended.'),
      ('How many teacher posts are there in Karnataka 2026?', '15,000: 9,000 GPT and Computer Science teacher posts, 4,950 Assistant Master and PE Grade-1 posts and 1,050 Primary School Teacher and PE Grade-2 posts.'),
      ('What is the GPSTR exam pattern in 2026?', 'Two compulsory OMR papers of 100 questions and 100 marks each, 2 hours each: Paper-1 General and Paper-2 in the subject, in Kannada and English. You need at least 35% in each paper.'),
      ('Is TET compulsory for Karnataka teacher recruitment?', 'For PST (TET Paper-1), GPT and Computer Science teacher posts (TET Paper-2), yes, and the TET score carries 20% weightage in the merit list. The guidelines say Assistant Masters and PE teachers (Grade-1 and Grade-2) do not need a TET certificate.'),
      ('Where can I practise GPSTR previous papers?', 'On Learn with Anil: the GPSTR 2022 Paper-1 General Studies with the department\'s key answers and explanations in Kannada and English, as a timed test or subject-wise practice.'),
    ])
ASOF_PAGE['karnataka-teacher-recruitment-notification-2026.html'] = '16 November 2026'


KP_ASOF = '22 November 2026'
NEW['karnataka-psi-notification-2026.html'] = dict(   # Anil, 22 Nov 2026: Karnataka Police SI PYQs; status page. Facts from KEA's PSI pages (PSIREC2024.aspx, PSI2023.aspx), read 22 Nov 2026
    exam='karnataka-police-si', board='KEA', site='ksp.karnataka.gov.in and cetonline.karnataka.gov.in/kea', crumb='Karnataka PSI 2026: notification status', faq_asof=KP_ASOF,
    title='Karnataka PSI Notification 2026 – Status, Last KSP PSI Exams (402 & 545 Posts), Pattern & Previous Papers | Learn with Anil',
    desc='Karnataka State Police Sub-Inspector (KSP PSI Civil) recruitment 2026: no new notification as of 22 November 2026. Facts of the last two written exams '
         'conducted by KEA (402 posts on 3 October 2024; the 545-post re-examination on 23 January 2024), the Paper-1 and Paper-2 pattern, and the PSI Paper-2 '
         'previous papers (2024 with KEA\'s final keys, plus KSP\'s 2017–2021 papers with their official keys) in Kannada and English, and the Rakshaka PSI mock tests.',
    h1='Karnataka PSI 2026: no new notification yet',
    lede='There is no new Karnataka State Police Sub-Inspector (Civil) notification as of 22 November 2026. The last two PSI written exams were conducted for KSP by the '
         'Karnataka Examinations Authority (KEA): the 402-post exam on 3 October 2024 and the 545-post re-examination on 23 January 2024. Below: the status, the facts '
         'of those two exams, the pattern, and the Paper-2 question papers of 2024, 2021, 2020, 2019 and 2017 with their official keys.',
    kn='ಕರ್ನಾಟಕ ಪೊಲೀಸ್ ಪಿಎಸ್‌ಐ (ಸಿವಿಲ್) ನೇಮಕಾತಿ 2026: 22 ನವೆಂಬರ್ 2026ರವರೆಗೆ ಹೊಸ ಅಧಿಸೂಚನೆ ಪ್ರಕಟವಾಗಿಲ್ಲ. ಕೆಇಎ ನಡೆಸಿದ 402 ಹುದ್ದೆಗಳ ಪರೀಕ್ಷೆ (3 ಅಕ್ಟೋಬರ್ 2024) ಮತ್ತು '
       '545 ಹುದ್ದೆಗಳ ಮರು ಪರೀಕ್ಷೆ (23 ಜನವರಿ 2024)ಯ ಪತ್ರಿಕೆ-2 ಕೀ ಉತ್ತರಗಳೊಂದಿಗೆ ಇಲ್ಲಿ ಅಭ್ಯಾಸಕ್ಕೆ ಲಭ್ಯ.',
    pdf='https://cetonline.karnataka.gov.in/keawebentry456/PSIREC2024/PSI_KEY_2024_kannada.pdf', pdfname='KEA, PSI 2024 (402 posts) Paper-2 final key answers (6 November 2024)',
    more_src=[('https://cetonline.karnataka.gov.in/kea/PSIREC2024.aspx', 'KEA: PSI recruitment 2024 (402 posts)'),
              ('https://cetonline.karnataka.gov.in/kea/PSI2023.aspx', 'KEA: PSI recruitment re-examination (545 posts)')],
    related=['ksp-constable-recruitment-2026.html'],
    sections=[
      ('Status (as of 22 November 2026)', 'table', [
        ('New KSP PSI notification', 'Not issued yet'),
        ('Who conducts the written exam', 'The Karnataka Examinations Authority (KEA), for the Karnataka State Police (as in 2024)'),
        ('Where to watch', 'ksp.karnataka.gov.in and cetonline.karnataka.gov.in/kea'),
        ('Last PSI written exam', '3 October 2024 (402 posts)')]),
      ('', 'note', 'Post numbers or dates for a 2026 PSI recruitment seen on some websites are not official until KSP or KEA publishes the notification.'),
      ('PSI (Civil) 402 posts, 2024 (KEA)', 'table', [
        ('Written exam', 'Thursday, 3 October 2024: Paper-1 (descriptive) and Paper-2 (objective)'),
        ('Paper-2 key answers', '4 October 2024, with an online objection window'),
        ('Final key and provisional results', '6 November 2024'),
        ('Final score list', '14 November 2024')]),
      ('PSI (Civil) 545 posts, re-examination (KEA)', 'table', [
        ('Why a re-examination', 'The original written exam of this recruitment was cancelled after irregularities came to light, and KEA held it afresh'),
        ('Written exam', 'Tuesday, 23 January 2024, in two sessions'),
        ('Provisional key', 'Published with a notice of 29 January 2024; the objection date was extended to 5 February 2024'),
        ('Final key answers', '1 March 2024'),
        ('Final score list', '28 March 2024')]),
      ('Written exam pattern', 'table+', (['Paper', 'What it has', 'Marks · time'], [
        ('Paper-1 (descriptive)', 'Essay, précis writing and translation (Kannada ↔ English)', '50 marks · 90 minutes'),
        ('Paper-2 (objective)', '100 multiple-choice questions on general knowledge, current affairs and mental ability, printed in Kannada and English', '150 marks (1.5 a question) · 90 minutes')])),
    ],
    faqs=[
      ('Is the Karnataka PSI notification 2026 out?', 'No, not as of 22 November 2026. The last KSP PSI written exam was held on 3 October 2024 for 402 posts.'),
      ('Who conducts the Karnataka PSI exam?', 'The Karnataka Examinations Authority (KEA) conducted both 2024 written exams (the 545-post re-examination and the 402-post exam) for the Karnataka State Police and published their keys and results.'),
      ('What is the Karnataka PSI exam pattern?', 'Paper-1 is descriptive (essay, précis and translation, 50 marks). Paper-2 has 100 objective questions in Kannada and English; in 2024 it carried 150 marks, 1.5 marks a question, with 90 minutes to answer.'),
      ('When was the Karnataka PSI re-exam held?', 'On 23 January 2024, for the 545 PSI (Civil) posts. KEA published the final key on 1 March 2024 and the final score list on 28 March 2024.'),
      ('Where can I practise Karnataka PSI previous papers?', 'On Learn with Anil: Paper-2 of the 3 October 2024 exam and of the 23 January 2024 re-examination, with KEA\'s final keys and explanations in Kannada and English, as 90-minute timed tests or subject-wise practice.'),
    ])
ASOF_PAGE['karnataka-psi-notification-2026.html'] = KP_ASOF

NEW['ksp-constable-recruitment-2026.html'] = dict(   # Anil, 22 Nov 2026: Karnataka Police Constable PYQs; status page. Facts from KEA's CPC/CAR-DAR pages (cpcrpc2026, cpckk2026, apcrpc, apckk) and news reports, 22 Nov 2026
    exam='karnataka-police-constable', board='KEA', site='ksp.karnataka.gov.in and cetonline.karnataka.gov.in/kea', crumb='KSP Constable 2026: status', faq_asof=KP_ASOF,
    title='KSP Police Constable 2026 – Civil (3,991 Posts) & CAR/DAR: Exam Dates, Keys, PET Stage, Pattern & Previous Papers | Learn with Anil',
    desc='Karnataka State Police constable recruitment 2026: Civil Police Constable (3,991 posts, written exam 2 August 2026) and Armed Police Constable CAR/DAR '
         '(written exam 6 September 2026), both conducted by KEA. Key dates, keys, the PET/ET and document verification stage, the exam pattern and both papers '
         'with answers in Kannada and English.',
    h1='KSP Police Constable 2026: written exams over, physical and document stage',
    lede='The Karnataka Examinations Authority (KEA) held the written exams of the Karnataka State Police\'s 2026 constable recruitments: Civil Police Constable on '
         '2 August 2026 and Armed Police Constable (CAR/DAR) on 6 September 2026, separately for the rest of Karnataka (RPC) and Kalyana Karnataka (KK). Below: '
         'the dates, the keys, the stage reached, the pattern, and the four question papers with answers.',
    kn='ಕರ್ನಾಟಕ ರಾಜ್ಯ ಪೊಲೀಸ್ ಕಾನ್ಸ್‌ಟೇಬಲ್ ನೇಮಕಾತಿ 2026: ಸಿವಿಲ್ ಪೊಲೀಸ್ ಕಾನ್ಸ್‌ಟೇಬಲ್ ಲಿಖಿತ ಪರೀಕ್ಷೆ 02.08.2026, ಸಶಸ್ತ್ರ ಪೊಲೀಸ್ ಕಾನ್ಸ್‌ಟೇಬಲ್ (ಸಿಎಆರ್/ಡಿಎಆರ್) 06.09.2026 — '
       'ಕೆಇಎ ಕೀ ಉತ್ತರಗಳೊಂದಿಗೆ ನಾಲ್ಕೂ ಪ್ರಶ್ನೆಪತ್ರಿಕೆಗಳು ಇಲ್ಲಿ ಅಭ್ಯಾಸಕ್ಕೆ ಲಭ್ಯ.',
    pdf='https://cetonline.karnataka.gov.in/kea/cpcrpc2026.aspx', pdfname='KEA: Civil Police Constable recruitment 2026 (RPC) page',
    more_src=[('https://cetonline.karnataka.gov.in/kea/cpckk2026.aspx', 'KEA: Civil Police Constable recruitment 2026 (Kalyana Karnataka)'),
              ('https://cetonline.karnataka.gov.in/kea/apcrpc.aspx', 'KEA: Armed Police Constable CAR/DAR 2026 (RPC)'),
              ('https://cetonline.karnataka.gov.in/kea/apckk.aspx', 'KEA: Armed Police Constable CAR/DAR 2026 (Kalyana Karnataka)')],
    related=['karnataka-psi-notification-2026.html'],
    sections=[
      ('Civil Police Constable 2026', 'table', [
        ('Posts', '3,991: 3,395 for the rest of Karnataka (RPC) and 596 for Kalyana Karnataka (KK), as reported'),
        ('Online application', '8 June to 3 July 2026, as reported'),
        ('Compulsory Kannada test', '19 July 2026'),
        ('Written exam', 'Sunday, 2 August 2026: RPC 10.30 am to 12 noon; KK 4.00 to 5.30 pm (time revised by KEA from 2.30 to 4.00 pm)'),
        ('Key answers', '3 August 2026; revised key 7 August 2026 after objections'),
        ('Provisional score lists', 'August 2026, district-wise'),
        ('PET and endurance test', 'Schedule published on 16 September 2026'),
        ('Document verification and medical test', 'Call letters from 20 November 2026')]),
      ('Armed Police Constable (CAR/DAR) 2026', 'table', [
        ('Notification', 'June 2026 (KEA notices of 19 and 22 June 2026)'),
        ('Written exam', 'Sunday, 6 September 2026: RPC 10.30 am to 12 noon; KK 3.00 to 4.30 pm'),
        ('Key answers', '7 September 2026; revised key 10 September 2026'),
        ('Final key and provisional score lists', '17 September 2026')]),
      ('Written exam pattern', 'table+', (['Paper', 'Questions · marks', 'Time'], [
        ('General Knowledge (Civil PC and CAR/DAR)', '100 questions · 100 marks, in Kannada and English', '90 minutes')])),
      ('', 'note', 'A quarter mark is deducted for each wrong answer. Candidates are shortlisted from the written exam for the physical tests (PST and endurance test); the '
                   'KSRP, IRB and KSISF constable recruitment is a separate exam.'),
    ],
    faqs=[
      ('When was the KSP civil police constable exam 2026?', 'On Sunday, 2 August 2026: 10.30 am to 12 noon for the rest of Karnataka (RPC) and 4.00 to 5.30 pm for Kalyana Karnataka, conducted by KEA.'),
      ('Is the KSP constable answer key out?', 'Yes. KEA published the Civil PC key on 3 August 2026 and a revised key on 7 August 2026; the CAR/DAR final key came on 17 September 2026.'),
      ('How many posts are in KSP civil police constable 2026?', '3,991, as reported: 3,395 for the rest of Karnataka and 596 for Kalyana Karnataka.'),
      ('What is the KSP constable exam pattern?', 'One General Knowledge paper of 100 questions and 100 marks in 90 minutes, printed in Kannada and English, with a quarter mark cut for each wrong answer.'),
      ('What stage is KSP constable 2026 at?', 'For Civil PC, KEA published the PET/ET schedule on 16 September 2026 and document verification and medical test call letters from 20 November 2026.'),
      ('Where can I practise KSP constable previous papers?', 'On Learn with Anil: the 2026 Civil PC (RPC and KK) and CAR/DAR (RPC and KK) papers with KEA\'s keys and explanations in Kannada and English, as 90-minute timed tests or subject-wise practice.'),
    ])
ASOF_PAGE['ksp-constable-recruitment-2026.html'] = KP_ASOF

NEW['mpsc-group-c-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: MPSC Group C (apply till 27 November; prelims 24 January 2027); facts from MPSC's own PDFs (in Marathi), read on 16 Nov 2026
    exam='mpsc-group-c', board='MPSC', site='mpsc.gov.in', crumb='MPSC Group C Notification 2026', faq_asof='16 November 2026',
    title='MPSC Group C Notification 2026: 16,717 Posts, Apply 13–27 November, Prelims 24 January 2027, Pattern & Previous Papers | Learn with Anil',
    desc='MPSC Group C 2026 (Advt. No. 017/2026): the corrigendum of 6 November 2026 raised the posts to 16,717 in 27 cadres, reopened online applications from 13 to 27 '
         'November 2026 (fee by 30 November) and moved the Group-C Combined Prelims to 24 January 2027. Cadre-wise posts, age limit, fee, exam pattern and MPSC Group C '
         'previous year papers with answers in Marathi and English.',
    h1='MPSC Group C notification 2026: 16,717 posts, prelims on 24 January 2027',
    lede='The Maharashtra Public Service Commission (MPSC) advertised the Maharashtra Group-C Services Combined Preliminary Examination 2026 (Advt. No. 017/2026) on '
         '25 June 2026 for 2,619 posts. Two corrigenda added cadres and posts, and the one of 6 November 2026 takes the total to 16,717 posts in 27 cadres, from Clerk-Typist '
         'and Talathi to Staff Nurse and Civil Engineering Assistant. Applications and cadre options are open again from 13 to 27 November 2026, and the prelims is now on '
         '24 January 2027. Below: the key dates, the posts, who can apply, the exam pattern and the MPSC Group C previous papers to practise.',
    mr='महाराष्ट्र लोकसेवा आयोग: महाराष्ट्र गट-क सेवा संयुक्त पूर्व परीक्षा-२०२६ (जाहिरात क्र. ०१७/२०२६) — शुद्धिपत्रक दि. ०६ नोव्हेंबर २०२६ नुसार २७ संवर्गांतील एकूण १६,७१७ पदे; '
       'अर्ज/विकल्प १३ ते २७ नोव्हेंबर २०२६, शुल्क ३० नोव्हेंबरपर्यंत; पूर्व परीक्षा २४ जानेवारी २०२७.',
    pdf='https://mpsc.gov.in/adv_notification/8', pdfname='MPSC Advt. No. 017/2026 and its corrigenda, mpsc.gov.in > Advertisements',
    more_src=[('https://mpsconline.gov.in', 'MPSC online application system (mpsconline.gov.in)'),
              ('https://mpsc.gov.in/prev_que_papers/9', 'MPSC previous question papers'), ('https://mpsc.gov.in/answer_keys_of_examinations/45', 'MPSC answer keys')],
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. 017/2026, 25 June 2026 (2,619 posts; first applications 27 June to 17 July 2026)'),
        ('Corrigenda', '16 July 2026 (offline OMR exam), 22 July 2026 (+3,088 posts, 5,707 in all), 1 August 2026 (exam pattern), 9 September 2026 (exam moved to 3 January 2027), '
                       '6 November 2026 (16,717 posts, new applications, exam moved to 24 January 2027), 13 November 2026 (qualifications for Craft Instructor and Civil Engineering Assistant)'),
        ('New applications and cadre options', '13 November 2026, 2 pm to 27 November 2026, 11.59 pm on mpsconline.gov.in'),
        ('Last date for the fee', '30 November 2026, 11.59 pm (online only: debit or credit card, net banking, UPI; the challan option is closed)'),
        ('Group-C Combined Prelims', 'Sunday, 24 January 2027, offline (OMR), at all district centres'),
        ('Main exam', 'Dates to be announced after the prelims result')]),
      ('Posts and vacancies (16,717)', 'table+', (['Cadre', 'Department', 'Posts'], [
        ('Clerk-Typist (लिपिक-टंकलेखक)', 'Various appointing authorities', '3,966'),
        ('Staff Nurse (अधिपरिचारिका)', 'Medical Education & Drugs', '3,911'),
        ('Village Revenue Officer (Talathi), Group-C', 'Revenue & Forest', '1,840'),
        ('Craft Instructor (शिल्प निदेशक)', 'Skills, Employment, Entrepreneurship & Innovation', '1,388'),
        ('Assistant Agriculture Officer', 'Agriculture, Animal Husbandry, Dairy Development & Fisheries', '1,203'),
        ('Civil Engineering Assistant', 'Water Resources 949 · Public Works 934', '1,883'),
        ('Assistant Motor Vehicle Inspector, Group-C', 'Home (Transport)', '461'),
        ('Livestock Supervisor', 'Agriculture, Animal Husbandry, Dairy Development & Fisheries', '322'),
        ('Tax Assistant', 'Finance', '282'),
        ('Assistant Fisheries Development Officer (Technical)', 'Agriculture, Animal Husbandry, Dairy Development & Fisheries', '254'),
        ('Mathematics & Drawing Instructor', 'Skills, Employment, Entrepreneurship & Innovation', '241'),
        ('Supply Inspector', 'Food & Civil Supplies', '214'),
        ('Senior Record Keeper / Senior Clerk / Record Keeper', 'Various departments', '196'),
        ('Assistant Storekeeper', 'Skills department 182 · Public Works 6', '188'),
        ('Junior Chemist', 'Water Supply & Sanitation', '153'),
        ('Other cadres (10)', 'Junior Education Extension Officer 58, Tribal Development Inspector 47, Investigator 42, Junior Skill, Employment & Guidance Officer 32, '
                              'Assistant Superintendent 11, Industry Inspector 9, Storekeeper 9, Technical Assistant 3, Deputy Accountant / Head Clerk 3, Telephone Operator 1', '215'),
        ('Total (27 cadres)', '', '16,717')])),
      ('', 'note', 'Candidates who applied earlier need not apply again; they can add the new cadres they qualify for as an option in "My Account" (no new fee). Posts received '
                   'from the government until the prelims result is final are also counted for the prelims result. The cadre-wise reservation is in Annexure-1 of the 6 November '
                   'corrigendum on mpsc.gov.in.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Marks'], [
        ('Combined Prelims (all cadres)', 'General Ability Test (सामान्य क्षमता चाचणी): 100 objective questions in Marathi and English, 1 hour; a quarter mark '
                                          'deducted for each wrong answer', '100'),
        ('Combined Main exam', 'One combined main exam for the administrative cadres that need a general degree (Clerk-Typist, Tax Assistant, Talathi and others)', '400'),
        ('Separate main exams', 'Technical cadres (such as AMVI, 300 marks, and Assistant Fisheries Development Officer) take their own main exam on their subject', 'by cadre')])),
      ('', 'note', 'The prelims syllabus covers current affairs, history (especially modern India and Maharashtra), geography (India and Maharashtra), the Indian Constitution '
                   'and polity, economy, general science, and intelligence test and arithmetic. The prelims only shortlists candidates for the main exam; the final selection '
                   'is on the main exam. The 2026 prelims was first advertised as a computer-based test; MPSC\'s corrigendum of 16 July 2026 made it an offline OMR exam.'),
      ('Who can apply', 'list', [
        'Indian citizen with a knowledge of Marathi. Most cadres need a degree from a recognised university; others need the qualification of their cadre '
        '(for example, Industry Inspector: an engineering or technology diploma or a science degree; AMVI: SSC and a 3-year diploma in automobile or mechanical engineering, '
        'with experience and driving licences as in the advertisement; Staff Nurse, Civil Engineering Assistant, Craft Instructor and Assistant Fisheries Development Officer: '
        'their professional qualification, listed in Annexure-3 of the 6 November corrigendum).',
        'Clerk-Typist and Tax Assistant: typing speed of at least 30 words a minute in Marathi and 40 in English (government commercial certificate or the equivalent '
        'computer typing course); some reserved categories get two years after appointment to pass it.',
        'Age as on 1 October 2026: at least 19 (18 for Tax Assistant); at most 38 years for the open category and 43 for backward classes, EWS and orphans, with more for '
        'sportspersons, ex-servicemen and persons with disabilities. A government resolution of 5 November 2026 relaxes the upper age limit by one more year.',
        'Prelims fee (not refundable): Rs. 394 for the open category, Rs. 294 for backward classes, EWS and orphans, Rs. 44 for ex-servicemen; bank charges extra.']),
    ],
    faqs=[
      ('What is the last date to apply for MPSC Group C 2026?', '27 November 2026 (11.59 pm) on mpsconline.gov.in; the fee can be paid online till 30 November 2026.'),
      ('When is the MPSC Group C prelims 2026 exam?', 'On 24 January 2027. It was first fixed for 25 October 2026, then for 3 January 2027; MPSC\'s corrigendum of 6 November 2026 moved it to 24 January 2027.'),
      ('How many vacancies are there in MPSC Group C 2026?', '16,717 posts in 27 cadres after the corrigendum of 6 November 2026 (the advertisement of 25 June 2026 had 2,619, and the corrigendum of 22 July 2026 raised it to 5,707).'),
      ('Do I need to apply again if I applied in June–July 2026?', 'No. Candidates who applied earlier keep their application and can add the new cadres they qualify for as options from "My Account", without paying the fee again.'),
      ('What is the MPSC Group C prelims exam pattern?', 'One objective paper, the General Ability Test: 100 questions, 100 marks, 1 hour, in Marathi and English, with a quarter mark deducted for each wrong answer.'),
      ('What is the age limit for MPSC Group C 2026?', '19 to 38 years for the open category and up to 43 for backward classes, EWS and orphans, as on 1 October 2026 (18 is the minimum for Tax Assistant), plus the one-year relaxation of 5 November 2026.'),
      ('What is the MPSC Group C application fee?', 'Rs. 394 for the open category, Rs. 294 for backward classes, EWS and orphans, and Rs. 44 for ex-servicemen, plus bank charges.'),
      ('Where can I practise MPSC Group C previous papers?', 'On Learn with Anil: the MPSC Group-C Combined Prelims 2025 and 2024 and the Group-B & C Combined Prelims 2023, with MPSC\'s final answer key and explanations in Marathi and English.'),
    ])
ASOF_PAGE['mpsc-group-c-notification-2026.html'] = '16 November 2026'

NEW['gsssb-cce-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: Gujarat GSSSB CCE 2.0 (apply till 30 November); facts from GSSSB's own PDFs (in Gujarati), read on 16 Nov 2026
    exam='gsssb-cce', board='GSSSB', site='gsssb.gujarat.gov.in', crumb='GSSSB CCE Notification 2026', faq_asof='16 November 2026',
    title='GSSSB CCE 2.0 Notification 2026: 1,237 Posts, Apply by 30 November, Exam Pattern, Age, Fee & Previous Papers | Learn with Anil',
    desc='GSSSB CCE 2.0 (Advt. No. 468/2026-27): 1,237 Class-III posts, 243 in Group-A (Senior Clerk, Head Clerk, Social Welfare Inspector, Sub Registrar and others) '
         'and 994 Junior Clerk posts in Group-B. Apply on ojas.gujarat.gov.in from 5 to 30 November 2026, fee by 2 December. Age, fee, the 150-mark prelims pattern '
         'and GSSSB CCE previous year papers with answers in Gujarati and English.',
    h1='GSSSB CCE 2.0 notification 2026: 1,237 posts, apply by 30 November',
    lede='The Gujarat Subordinate Service Selection Board (GSSSB) has advertised its second Combined Competitive Examination under the new rules, "CCE 2.0" '
         '(Advt. No. 468/2026-27), for 1,237 Class-III posts: 243 Group-A posts in eight cadres and 994 Junior Clerk posts in Group-B. Online applications on '
         'ojas.gujarat.gov.in are open from 5 November (2 pm) to 30 November 2026 (11.59 pm). Below: the key dates, the posts, who can apply, the exam pattern '
         'and the GSSSB CCE previous papers to practise.',
    gu='ગુજરાત ગૌણ સેવા પસંદગી મંડળ: ગુજરાત ગૌણ સેવા વર્ગ-૩ (ગ્રુપ-A તથા ગ્રુપ-B) સંયુક્ત સ્પર્ધાત્મક પરીક્ષા, જાહેરાત ક્રમાંક ૪૬૮/૨૦૨૬૨૭ — કુલ ૧,૨૩૭ જગ્યાઓ '
       '(ગ્રુપ-A ૨૪૩, ગ્રુપ-B જુનિયર ક્લાર્ક ૯૯૪); ઓનલાઇન અરજી ૫ થી ૩૦ નવેમ્બર ૨૦૨૬, ફી ૨ ડિસેમ્બર ૨૦૨૬ સુધી; પ્રાથમિક પરીક્ષા ૧૫૦ ગુણ, ૧૨૦ મિનિટ.',
    pdf='https://gsssb.gujarat.gov.in', pdfname='GSSSB Advt. No. 468/2026-27, gsssb.gujarat.gov.in > Advertisement',
    more_src=[('https://ojas.gujarat.gov.in', 'OJAS, the Gujarat government online application site (ojas.gujarat.gov.in)')],
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. 468/2026-27, Gujarat Subordinate Services Class-III (Group-A and Group-B) Combined Competitive Examination'),
        ('Online applications', '5 November 2026, 2 pm to 30 November 2026, 11.59 pm on ojas.gujarat.gov.in'),
        ('Last date for the fee', '2 December 2026, 11.59 pm (online only)'),
        ('Preliminary exam', 'Computer-based (MCQ); GSSSB will announce the date'),
        ('Main exam', 'After the prelims result: descriptive for Group-A, objective (MCQ) for Group-B')]),
      ('Posts and vacancies (1,237)', 'table+', (['Post (Class-III)', 'Office', 'Posts'], [
        ('Sub Registrar, Grade-1', 'Inspector General of Registration', '6'),
        ('Sub Registrar, Grade-2', 'Inspector General of Registration', '15'),
        ('Assistant Tribal Development Officer', 'Director, Tribal Development', '50'),
        ('Social Welfare Inspector', 'Director, Developing Castes Welfare', '89'),
        ('Office Superintendent', 'Director, Prohibition & Excise', '7'),
        ('Office Assistant', 'Gujarat Public Service Commission', '15'),
        ('Head Clerk', 'Various heads of department', '10'),
        ('Senior Clerk', 'Various heads of department', '51'),
        ('Total Group-A', '', '243'),
        ('Junior Clerk (Group-B)', 'Various heads of department', '994'),
        ('Total', '', '1,237')])),
      ('', 'note', 'Fixed pay for the first five years: Rs. 49,600 a month for Sub Registrar Grade-1, Office Superintendent and Assistant Tribal Development Officer; '
                   'Rs. 40,800 for Sub Registrar Grade-2, Social Welfare Inspector and Head Clerk; Rs. 26,000 for Senior Clerk, Office Assistant and Junior Clerk. '
                   'The category-wise reservation of each post is in the advertisement.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Marks'], [
        ('Preliminary (Group-A and Group-B together)', '150 objective questions in 120 minutes: Reasoning 60, Quantitative Aptitude 30, General Awareness and Current '
                                                       'Affairs 30, English 15, Gujarati 15; 0.25 mark deducted for each wrong answer', '150'),
        ('Main exam, Group-A (descriptive)', 'Paper I Gujarati Language Skill (100), Paper II English Language Skill (100), Paper III General Studies (150), 3 hours each', '350'),
        ('Main exam, Group-B (objective)', '120 minutes: Constitution 20, Economy 20, Public Administration 20, Ethics 10, Government Schemes 30, Current Affairs 30, '
                                           'History & Geography of Gujarat 20, Cultural Heritage of Gujarat 10, Gujarati & English 20, Science, Environment & IT 20', '200'),
      ])),
      ('', 'note', 'The prelims is only a screening test: its marks are not counted for the final list. Group-A and Group-B have separate lists, and about seven times the '
                   'posts in each category are called to the main exam. The minimum qualifying mark is 40% in each stage. GSSSB\'s earlier CCE prelims (Advt. 212/2023-24, '
                   'held in April–May 2024) had 100 questions in 60 minutes; the papers on this site are from that exam.'),
      ('Who can apply', 'list', [
        'Indian citizen with a graduate degree from a recognised university, a basic knowledge of computers as in the Gujarat Civil Services rules of 1967, and an '
        'adequate knowledge of Gujarati or Hindi or both.',
        'Age as on 30 November 2026: 20 to 35 years. Relaxation: 5 years for women of the general category and for men of the reserved categories, 10 years for women of '
        'the reserved categories and for men with disabilities, up to an upper age of 45; ex-servicemen get their service period plus 3 years.',
        'Prelims fee: Rs. 500 for the unreserved category; Rs. 400 for all women, SEBC, SC, ST, EWS, persons with disabilities and ex-servicemen. GSSSB refunds the fee '
        'to candidates who appear in the exam.']),
    ],
    faqs=[
      ('What is the last date to apply for GSSSB CCE 2.0?', '30 November 2026 (11.59 pm) on ojas.gujarat.gov.in; the fee can be paid online till 2 December 2026.'),
      ('How many posts are there in GSSSB CCE 2.0?', '1,237: 243 Group-A posts (Senior Clerk 51, Social Welfare Inspector 89, Assistant Tribal Development Officer 50 and others) and 994 Junior Clerk posts in Group-B.'),
      ('What is the GSSSB CCE 2.0 prelims exam pattern?', '150 objective questions for 150 marks in 120 minutes: Reasoning 60, Quantitative Aptitude 30, General Awareness and Current Affairs 30, English 15 and Gujarati 15, with 0.25 mark cut for each wrong answer.'),
      ('What is the age limit for GSSSB CCE 2.0?', '20 to 35 years as on 30 November 2026, with relaxations for women, reserved categories, persons with disabilities and ex-servicemen up to an upper age of 45.'),
      ('What is the GSSSB CCE application fee?', 'Rs. 500 for the unreserved category and Rs. 400 for women, SEBC, SC, ST, EWS, persons with disabilities and ex-servicemen; it is refunded to those who appear in the exam.'),
      ('When is the GSSSB CCE 2.0 exam date?', 'GSSSB has not announced the prelims date yet; it will be on gsssb.gujarat.gov.in.'),
      ('Where can I practise GSSSB CCE previous papers?', 'On Learn with Anil: GSSSB\'s own CCE Preliminary papers of 2024 (Advt. 212/2023-24) with its final answers and explanations in Gujarati and English.'),
    ])
ASOF_PAGE['gsssb-cce-notification-2026.html'] = '16 November 2026'

NEW['upsssc-inter-level-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: UP UPSSSC Inter level (apply till 1 December); facts from UPSSSC's own advertisement (in Hindi), read on 16 Nov 2026
    exam='upsssc-inter-level', board='UPSSSC', site='upsssc.gov.in', crumb='UPSSSC Inter Level Mains Notification 2026', faq_asof='16 November 2026',
    title='UPSSSC Inter Level Mains Notification 2026: 1,784 Posts, Apply by 1 December, Exam Pattern & Previous Papers | Learn with Anil',
    desc='UPSSSC Advt. No. 26-Exam/2026, Combined Lower Subordinate (Intermediate Level) Mains for PET-2025 candidates: 1,784 posts including Gram Vikas Adhikari 525, '
         'Gram Panchayat Adhikari 508 and Vanijya Kar Sangrah Amin 235. Apply on upsssc.gov.in from 10 November to 1 December 2026. Posts, eligibility, exam '
         'pattern and UPSSSC Mains previous papers with answers in Hindi and English.',
    h1='UPSSSC Inter level Mains notification 2026: 1,784 posts, apply by 1 December',
    lede='The Uttar Pradesh Subordinate Services Selection Commission (UPSSSC) has advertised its Combined Lower Subordinate Services (Intermediate Level) Mains '
         '(Advt. No. 26-Exam/2026, published 16 October 2026) for 1,784 posts in twelve cadres, from Gram Vikas Adhikari and Gram Panchayat Adhikari to Vanijya Kar '
         'Sangrah Amin. Only candidates with a PET-2025 score card can apply, on upsssc.gov.in from 10 November to 1 December 2026. Below: the key dates, the posts, '
         'who can apply, the exam pattern and UPSSSC Mains previous papers to practise.',
    hi='उत्तर प्रदेश अधीनस्थ सेवा चयन आयोग: विज्ञापन संख्या-26-परीक्षा/2026, संयुक्त अवर अधीनस्थ सेवा (इण्टरमीडिएट स्तरीय) मुख्य परीक्षा (प्रा.अ.प.-2025)/26 — कुल 1784 पद; '
       'ऑनलाइन आवेदन 10 नवम्बर से 01 दिसम्बर 2026, शुल्क समायोजन एवं संशोधन 08 दिसम्बर 2026 तक; केवल PET-2025 स्कोर कार्ड धारक अभ्यर्थी।',
    pdf='https://upsssc.gov.in', pdfname='UPSSSC Advt. No. 26-Exam/2026, upsssc.gov.in > Advertisements',
    more_src=[],
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. 26-Exam/2026, Combined Lower Subordinate Services (Intermediate Level) Mains Examination (PET-2025)/26, published 16 October 2026'),
        ('Online applications', '10 November to 1 December 2026 on upsssc.gov.in (registration, fee and final submission)'),
        ('Fee adjustment and corrections', 'Up to 8 December 2026'),
        ('Mains', 'UPSSSC will announce the date; candidates are shortlisted on their PET-2025 normalised score'),
      ]),
      ('Posts and vacancies (1,784)', 'table+', (['Post', 'Department', 'Posts'], [
        ('Gram Vikas Adhikari (Samaj Kalyan)', 'Social Welfare Directorate', '525'),
        ('Gram Panchayat Adhikari', 'Panchayati Raj Directorate', '508'),
        ('Vanijya Kar Sangrah Amin', 'State Tax Commissioner\'s office', '235'),
        ('Bhumi Arjan Amin', 'Land Acquisition Directorate, Revenue Board', '187'),
        ('Samaj Kalyan Paryavekshak', 'Social Welfare Directorate', '137'),
        ('Bhandar Pal evam Lipik', 'Medical & Health Services Directorate (118 + 2 special recruitment)', '120'),
        ('Sahakari Krishi Paryavekshak', 'Commissioner & Registrar, Cooperatives', '50'),
        ('Saraniyak', 'Consolidation Commissioner\'s office', '14'),
        ('Grihmata', 'Tribal Development Directorate', '5'),
        ('Farm Lipik and Bikri Karta', 'Jail Administration & Reform Services', '3'),
        ('Total', '', '1,784')])),
      ('', 'note', 'Pay: Level-3 (Rs. 21,700–69,100) for Gram Vikas Adhikari, Gram Panchayat Adhikari, Vanijya Kar Sangrah Amin, Bhumi Arjan Amin, Samaj Kalyan '
                   'Paryavekshak, Sahakari Krishi Paryavekshak and Grihmata; Level-2 for the other posts. The category-wise reservation of each post is in the advertisement.'),
      ('Exam pattern', 'table+', (['Part', 'Subjects', 'Questions'], [
        ('Part 1', 'History & National Movement 5, Polity & Constitution 5, Geography 5, Indian Economy & Social Development 5, Rural Society & Development 5, '
                   'Current Affairs 5, Science & Technology 5, Environment, Ecology & Disaster Management 10, Data Interpretation 10, General Hindi 10', '65'),
        ('Part 2', 'Computer & Information Technology', '15'),
        ('Part 3', 'Uttar Pradesh General Knowledge', '20'),
        ('Total', 'One objective paper, 100 marks, 2 hours; a quarter mark deducted for each wrong answer', '100')])),
      ('', 'note', 'UPSSSC used this pattern (five options per question, in Hindi and English) in its Lekhpal Mains of 21 May 2026 and its Graduate-level Mains of '
                   '23 August 2026; their papers, with UPSSSC\'s revised answer keys, are on this site.'),
      ('Who can apply', 'list', [
        'Only candidates who appeared in UPSSSC\'s Preliminary Eligibility Test 2025 (PET-2025) and were issued its score card; those with a zero or negative score are not shortlisted.',
        'The essential qualification of the post as given in the advertisement.',
        'Age: 18 to 40 years as on 1 July 2026, with the relaxations of Uttar Pradesh government rules for reserved categories.',
        'Fee: only the online processing fee of Rs. 25 is charged with the application, for every category; candidates shortlisted for the Mains pay the Mains fee separately before downloading the admit card.']),
    ],
    faqs=[
      ('What is the last date to apply for UPSSSC Inter level Mains 2026?', '1 December 2026 on upsssc.gov.in; fee adjustment and corrections are allowed till 8 December 2026.'),
      ('How many posts are there in UPSSSC Advt. 26-Exam/2026?', '1,784, including Gram Vikas Adhikari 525, Gram Panchayat Adhikari 508, Vanijya Kar Sangrah Amin 235 and Bhumi Arjan Amin 187.'),
      ('Who can apply for the UPSSSC Inter level Mains?', 'Only candidates with a UPSSSC PET-2025 score card and the qualification of the post; they are shortlisted for the Mains on their PET-2025 normalised score.'),
      ('What is the UPSSSC Inter level Mains exam pattern?', 'One objective paper of 100 questions in 2 hours with a quarter mark negative: general studies and General Hindi 65, Computer 15 and UP GK 20.'),
      ('What is the age limit?', '18 to 40 years as on 1 July 2026, with the usual UP relaxations for reserved categories.'),
      ('Where can I practise UPSSSC Mains previous papers?', 'On Learn with Anil: the Lekhpal Mains 2026, the Lower Subordinate (Graduate Level) Mains 2026 and the Gram Panchayat Adhikari Mains 2025, with UPSSSC\'s revised answer keys and explanations in Hindi and English.'),
    ])
ASOF_PAGE['upsssc-inter-level-notification-2026.html'] = '16 November 2026'

NEW['uppsc-ro-aro-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: UPPSC RO/ARO (apply till 26 November); facts from UPPSC's own advertisement A-4/E-1/2026, read on 16 Nov 2026
    exam='uppsc-ro-aro', board='UPPSC', site='uppsc.up.nic.in', crumb='UPPSC RO/ARO Notification 2026', faq_asof='16 November 2026',
    title='UPPSC RO/ARO Notification 2026: 501 Posts, Apply by 26 November, Age, Fee, Exam Pattern & Previous Papers | Learn with Anil',
    desc='UPPSC Samiksha Adhikari / Sahayak Samiksha Adhikari (RO/ARO) Examination-2026, Advt. A-4/E-1/2026: 501 posts in the UP Secretariat, UPPSC, Board of Revenue '
         'and the Advocate General\'s office. Apply on uppsc.up.nic.in from 26 October to 26 November 2026. Age 21–40, fee, the 200-question prelims pattern and '
         'UPPSC RO/ARO previous papers with answers in Hindi and English.',
    h1='UPPSC RO/ARO notification 2026: 501 posts, apply by 26 November',
    lede='The Uttar Pradesh Public Service Commission (UPPSC) has advertised the Samiksha Adhikari / Sahayak Samiksha Adhikari Etc. (General / Special Recruitment) '
         'Examination-2026 (Advt. No. A-4/E-1/2026, 26 October 2026) for 501 posts. Online applications, with a One Time Registration (OTR) number, are open on '
         'uppsc.up.nic.in from 26 October to 26 November 2026. Below: the key dates, the posts, who can apply, the exam pattern and the UPPSC RO/ARO previous papers to practise.',
    hi='उत्तर प्रदेश लोक सेवा आयोग: समीक्षा अधिकारी/सहायक समीक्षा अधिकारी आदि (सामान्य/विशेष चयन) परीक्षा-2026, विज्ञापन संख्या A-4/E-1/2026 — कुल 501 पद; '
       'ऑनलाइन आवेदन 26 अक्टूबर से 26 नवम्बर 2026, संशोधन 03 दिसम्बर 2026 तक; प्रारंभिक परीक्षा 200 प्रश्न (सामान्य अध्ययन 140, सामान्य हिंदी 60), 3 घंटे।',
    pdf='https://uppsc.up.nic.in', pdfname='UPPSC Advt. No. A-4/E-1/2026, uppsc.up.nic.in > All Notifications/Advertisements',
    more_src=[('https://otr.pariksha.nic.in', 'One Time Registration (OTR) portal')],
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. A-4/E-1/2026, 26 October 2026'),
        ('Online applications', '26 October to 26 November 2026 on uppsc.up.nic.in (an OTR number from otr.pariksha.nic.in is needed first)'),
        ('Last date for the fee', '26 November 2026'),
        ('Corrections and fee reconciliation', 'Up to 3 December 2026'),
        ('Prelims', 'UPPSC will announce the date'),
      ]),
      ('Posts and vacancies (501)', 'table+', (['Post', 'Office', 'Posts'], [
        ('Samiksha Adhikari', 'U.P. Secretariat 122 · UPPSC 3 · Board of Revenue 6', '131'),
        ('Samiksha Adhikari (Account)', 'U.P. Secretariat', '31'),
        ('Sahayak Samiksha Adhikari', 'U.P. Secretariat 261 · UPPSC 21 · Board of Revenue 2 · Office of the Advocate General 45', '329'),
        ('Sahayak Samiksha Adhikari (Account), special recruitment', 'U.P. Secretariat', '6'),
        ('Manager, Care-Taker, Receptionist, Store Keeper', 'UPPSC (1 each)', '4'),
        ('Total', '', '501')])),
      ('', 'note', 'Pay scales from Rs. 29,200–64,700 (Level 5) to Rs. 47,600–1,51,100 (Level 8), as in the advertisement. The category-wise posts are in the advertisement; '
                   'the number of vacancies may change before the prelims result.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Marks'], [
        ('Prelims (screening)', 'One objective paper, 3 hours: General Studies 140 questions and General Hindi 60 questions, 1 mark each; four options, one third of a '
                                'mark deducted for each wrong answer', '200'),
        ('Mains (written)', 'Selection is on the total marks of the Mains; fifteen times the vacancies are called from the prelims', 'as notified'),
      ])),
      ('', 'note', 'General Studies covers general science, history of India and the national movement, polity, economy and culture, agriculture, commerce and '
                   'trade, population, ecology and urbanisation, world and Indian geography, current events, general intelligence and Uttar Pradesh. General Hindi '
                   'covers opposites, sentence correction, one-word substitution, words of similar use, nouns and adjectives, and synonyms.'),
      ('Who can apply', 'list', [
        'A bachelor\'s degree. Sahayak Samiksha Adhikari posts also need a computer qualification (such as the NIELIT \'O\' Level) and a Hindi typing speed of '
        '25 words a minute; the Account posts need a B.Com. with accountancy. Check the exact qualification of each post in the advertisement.',
        'Age: 21 to 40 years as on 1 July 2026 (born between 2 July 1986 and 1 July 2005); 5 years more for SC, ST and OBC of U.P., 15 years more for persons with '
        'disabilities, and the rules\' relaxation for ex-servicemen.',
        'Fee (exam fee + Rs. 25 online processing fee): Rs. 125 for unreserved, EWS and OBC; Rs. 65 for SC, ST and ex-servicemen; Rs. 25 for persons with disabilities.']),
    ],
    faqs=[
      ('What is the last date to apply for UPPSC RO/ARO 2026?', '26 November 2026 on uppsc.up.nic.in, which is also the last date for the fee; corrections are allowed till 3 December 2026.'),
      ('How many posts are there in UPPSC RO/ARO 2026?', '501: 131 Samiksha Adhikari, 31 Samiksha Adhikari (Account), 329 Sahayak Samiksha Adhikari, 6 Sahayak Samiksha Adhikari (Account) in special recruitment and 4 other UPPSC posts.'),
      ('What is the UPPSC RO/ARO prelims exam pattern?', 'One objective paper of 200 questions in 3 hours: General Studies 140 and General Hindi 60, with one third of a mark cut for each wrong answer.'),
      ('What is the age limit for UPPSC RO/ARO 2026?', '21 to 40 years as on 1 July 2026, with 5 more years for SC, ST and OBC of U.P. and 15 more for persons with disabilities.'),
      ('What is the UPPSC RO/ARO application fee?', 'Rs. 125 for unreserved, EWS and OBC, Rs. 65 for SC, ST and ex-servicemen, and Rs. 25 for persons with disabilities (including the Rs. 25 processing fee).'),
      ('Where can I practise UPPSC RO/ARO previous papers?', 'On Learn with Anil: the 27 July 2025 prelims (200 questions, UPPSC\'s own booklet with its key) and the 2021 General Studies and General Hindi papers, with explanations in Hindi and English.'),
    ])
ASOF_PAGE['uppsc-ro-aro-notification-2026.html'] = '16 November 2026'

NEW['ukpsc-lower-pcs-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: Uttarakhand Lower PCS (apply till 26 November); facts from UKPSC's own advertisement A-1/E-2/DR/LSS/2026-27 and notice of 6 Nov 2026, read on 16 Nov 2026
    exam='ukpsc-lower-pcs', board='UKPSC', site='psc.uk.gov.in', crumb='UKPSC Lower PCS Notification 2026', faq_asof='16 November 2026',
    title='UKPSC Lower PCS Notification 2026: 54 Posts, Apply by 26 November, Age, Fee, Exam Pattern & Previous Papers | Learn with Anil',
    desc='Uttarakhand Combined State (Civil) Lower Subordinate Service Exam-2026 (UKPSC Lower PCS), Advt. A-1/E-2/DR/LSS/2026-27: 54 posts including Naib Tehsildar, '
         'Excise Inspector and Marketing Inspector. Apply on psc.uk.gov.in from 6 to 26 November 2026. Age 21–42, fee, the 150-question prelims pattern and UKPSC '
         'Lower PCS previous papers with answers in Hindi and English.',
    h1='UKPSC Lower PCS notification 2026: 54 posts, apply by 26 November',
    lede='The Uttarakhand Public Service Commission (UKPSC), Haridwar, has advertised the Uttarakhand Combined State (Civil) Lower Subordinate Service Examination-2026 '
         '(Advt. No. A-1/E-2/DR/LSS/2026-27, 6 November 2026) for 54 posts. Online applications are open on psc.uk.gov.in from 6 to 26 November 2026. Below: the key '
         'dates, the posts, who can apply, the exam pattern and the UKPSC Lower PCS previous papers to practise.',
    hi='उत्तराखण्ड लोक सेवा आयोग: उत्तराखण्ड सम्मिलित राज्य (सिविल) अवर अधीनस्थ सेवा परीक्षा-2026, विज्ञापन संख्या A-1/E-2/DR/LSS/2026-27 — कुल 54 पद; '
       'ऑनलाइन आवेदन 06 से 26 नवम्बर 2026 (रात्रि 11:59 बजे तक), संशोधन 03 से 12 दिसम्बर 2026; प्रारंभिक परीक्षा: सामान्य अध्ययन एवं सामान्य अभिरुचि परीक्षण, 150 प्रश्न, 2 घंटे।',
    pdf='https://psc.uk.gov.in', pdfname='UKPSC Advt. No. A-1/E-2/DR/LSS/2026-27, psc.uk.gov.in > Candidate Corner > Recruitment',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. A-1/E-2/DR/LSS/2026-27, 6 November 2026 (notice No. 235/03/E-2/DR/LSS/2026-27)'),
        ('Online applications', '6 to 26 November 2026 (11:59 pm) on psc.uk.gov.in'),
        ('Last date for the fee (net banking, card or UPI)', '26 November 2026 (11:59 pm)'),
        ('Corrections to the online form', '3 to 12 December 2026 (11:59 pm)'),
        ('Prelims', 'UKPSC will announce the date'),
      ]),
      ('Posts and vacancies (54)', 'table+', (['Post', 'Department', 'Posts'], [
        ('Naib Tehsildar', 'Revenue (Level 7)', '13'),
        ('Excise Inspector', 'Excise (Level 7)', '4'),
        ('Supply Inspector', 'Food, Civil Supply and Consumer Affairs (Level 6)', '2'),
        ('Marketing Inspector', 'Food, Civil Supply and Consumer Affairs (Level 6)', '20'),
        ('Labour Enforcement Officer', 'Labour (Level 6)', '5'),
        ('Tax Officer, Zila Panchayat', 'Panchayati Raj (Level 6)', '5'),
        ('Senior Cane Development Inspector', 'Sugarcane Development & Sugar Industry (Level 6)', '1'),
        ('Cane Development Inspector', 'Sugarcane Development & Sugar Industry (Level 5)', '4'),
        ('Total', '', '54')])),
      ('', 'note', 'Pay: Level 7 is Rs. 44,900–1,42,400, Level 6 Rs. 35,400–1,12,400 and Level 5 Rs. 29,200–92,300. The category-wise and horizontal reservation of each '
                   'post is in the advertisement; the number of vacancies may change.'),
      ('Exam pattern', 'table+', (['Stage', 'Paper', 'Marks'], [
        ('Prelims (objective)', 'General Studies & General Aptitude Test: 150 questions, 2 hours; a quarter of a question\'s marks deducted for each wrong answer. '
                                'Prelims marks only decide who goes to the Mains', '150'),
        ('Mains (descriptive)', 'Language (General Hindi) 100, 2 hours (35% needed); Essay 100, 2 hours; General Studies Paper I 200, 3 hours; General Studies Paper II 200, 3 hours', '600'),
        ('Personality test', 'Interview', '75'),
      ])),
      ('', 'note', 'The Mains is held at Haldwani and Haridwar. The full syllabus is in Appendix 2 of the advertisement.'),
      ('Who can apply', 'list', [
        'A bachelor\'s degree from a recognised university; the two Cane Development Inspector posts need a bachelor\'s degree in agriculture. Naib Tehsildar and '
        'Excise Inspector have height and chest standards; two years in the Territorial Army or an NCC \'B\' certificate gets preference.',
        'Age: 21 to 42 years as on 1 July 2026 (born between 2 July 1984 and 1 July 2005); 5 years more for SC, ST and OBC of Uttarakhand and dependants of '
        'freedom fighters, 10 years more for persons with disabilities of Uttarakhand, and the rules\' relaxation for ex-servicemen.',
        'Fee (application fee + Rs. 16.36 processing fee): Rs. 166.36 for unreserved, EWS and OBC of Uttarakhand; Rs. 76.36 for SC, ST and persons with disabilities '
        'of Uttarakhand; no fee for orphans living in the state\'s children\'s homes.']),
    ],
    faqs=[
      ('What is the last date to apply for UKPSC Lower PCS 2026?', '26 November 2026 (11:59 pm) on psc.uk.gov.in, which is also the last date for the fee; corrections are allowed from 3 to 12 December 2026.'),
      ('How many posts are there in UKPSC Lower PCS 2026?', '54: Naib Tehsildar 13, Excise Inspector 4, Supply Inspector 2, Marketing Inspector 20, Labour Enforcement Officer 5, Tax Officer (Zila Panchayat) 5, Senior Cane Development Inspector 1 and Cane Development Inspector 4.'),
      ('What is the UKPSC Lower PCS prelims exam pattern?', 'One objective paper, General Studies & General Aptitude Test, of 150 questions for 150 marks in 2 hours, with a quarter of a question\'s marks cut for each wrong answer.'),
      ('What is the age limit for UKPSC Lower PCS 2026?', '21 to 42 years as on 1 July 2026, with 5 more years for SC, ST and OBC of Uttarakhand and 10 more for persons with disabilities.'),
      ('What is the UKPSC Lower PCS application fee?', 'Rs. 166.36 for unreserved, EWS and OBC, and Rs. 76.36 for SC, ST and persons with disabilities of Uttarakhand (including the Rs. 16.36 processing fee).'),
      ('Where can I practise UKPSC Lower PCS previous papers?', 'On Learn with Anil: the Lower PCS prelims 2024 and 2021 and the RO/ARO prelims 2023 (UKPSC\'s own booklets with its final keys), with explanations in Hindi and English.'),
    ])
ASOF_PAGE['ukpsc-lower-pcs-notification-2026.html'] = '16 November 2026'

NEW['cg-vyapam-group-2-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: Chhattisgarh Vyapam Group 2 (apply till 27 November); facts from CGSSB's detailed advertisement, press note and syllabus of 5 Nov 2026, read on 16 Nov 2026
    exam='cg-vyapam-group-2', board='CG Vyapam', site='cgssb.cgstate.gov.in', crumb='CG Vyapam Group 2 Notification 2026', faq_asof='16 November 2026',
    title='CG Vyapam Group 2 Notification 2026: 1,703 Posts (Assistant Grade 3, Steno, DEO, ASI), Apply by 27 November, Exam 10 January | Learn with Anil',
    desc='Chhattisgarh Karmchari Chayan Mandal (CGSSB, formerly CG Vyapam) Group-2 Sub-group-02 exam (G20227): 1,703 posts including 1,206 Assistant Grade-3, ASI, '
         'stenographers and data entry operators. Apply on cgssb.cgstate.gov.in from 5 to 27 November 2026; exam on 10 January 2027. Eligibility, fee, the 100-question '
         'pattern and CG Vyapam previous papers with answers in Hindi and English.',
    h1='CG Vyapam Group 2 notification 2026: 1,703 posts, apply by 27 November',
    lede='The Chhattisgarh Karmchari Chayan Mandal (CGSSB, which has taken over from CG Vyapam) has advertised the written exam for the Group-2, Class III (postgraduate '
         'and graduate level) Sub-group-02 posts (exam code G20227) on 5 November 2026: 1,703 posts in all. Online applications are open on cgssb.cgstate.gov.in from 5 to '
         '27 November 2026, and the exam is on 10 January 2027. Below: the key dates, the posts, who can apply, the exam pattern and the CG Vyapam previous papers to practise.',
    hi='छत्तीसगढ़ कर्मचारी चयन मण्डल: समूह-2 तृतीय श्रेणी (स्नातकोत्तर एवं स्नातक स्तर) उप समूह-02 लिखित भर्ती परीक्षा (G20227) — कुल 1,703 पद (सहायक ग्रेड-3: 1,206); '
       'ऑनलाइन आवेदन 05 से 27 नवम्बर 2026 (सायं 5 बजे तक), त्रुटि सुधार 28 से 30 नवम्बर 2026; परीक्षा 10 जनवरी 2027 (रविवार), 10:00 से 12:15 बजे; 100 प्रश्न, 2 घंटे।',
    pdf='https://cgssb.cgstate.gov.in', pdfname='CGSSB detailed advertisement No. SSB/Pariksha F-20/2026 of 5 November 2026 (G20227), cgssb.cgstate.gov.in',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement and press note', '5 November 2026 (exam code G20227)'),
        ('Online applications', '5 to 27 November 2026 (5 pm) on cgssb.cgstate.gov.in'),
        ('Corrections to the online form', '28 to 30 November 2026 (5 pm)'),
        ('Admit cards (expected)', '4 January 2027'),
        ('Written exam', 'Sunday, 10 January 2027, 10:00 am to 12:15 pm, at the 5 divisional headquarters'),
      ]),
      ('Posts and vacancies (1,703)', 'table+', (['Post', 'Posts'], [
        ('Assistant Grade-3', '1,206'),
        ('Assistant Sub-Inspector-A (District-unit cadre)', '279'),
        ('Registration Clerk', '50'),
        ('Assistant Sub-Inspector-A (General Branch)', '40'),
        ('Sub-Inspector-A (Stenographer) (General Branch) (Hindi)', '34'),
        ('Stenographer (Hindi)', '30'),
        ('Data Entry Operator', '25'),
        ('Steno Typist', '23'),
        ('Stenographer (Bilingual)', '13'),
        ('Stenographer (English)', '3'),
        ('Total', '1,703')])),
      ('', 'note', 'Candidates choose their posts and departments in order of preference in the online form, and the choice cannot be changed later. The post codes, '
                   'departments and category-wise vacancies are in the advertisement.'),
      ('Exam pattern', 'table+', (['Part', 'Subject', 'Questions (marks)'], [
        ('1', 'General knowledge of computers', '20'),
        ('2', '(a) General Studies · (b) General knowledge of Chhattisgarh', '20 + 20'),
        ('3', 'General Mental Ability', '10'),
        ('4', 'General Mathematics', '10'),
        ('5', 'General Hindi', '10'),
        ('6', 'General English', '10'),
        ('Total', 'Objective, 2 hours, in Hindi and English (except the language parts); 1 mark a question, a quarter mark cut for each wrong answer', '100'),
      ])),
      ('', 'note', 'Minimum qualifying marks: 33% for unreserved and 23% for reserved categories and persons with disabilities. For the 7 Home and Police posts, 15 times '
                   'the vacancies are called to a qualifying physical measurement test; the final allotment is on the written marks, the post preferences and the '
                   'reservation rules.'),
      ('Who can apply', 'list', [
        'A bachelor\'s degree with a one-year computer diploma, or 10+2 with the Modern Office Management (MOM) diploma of a Chhattisgarh polytechnic, plus a skill '
        'certificate from the Chhattisgarh Shorthand-Typing-Computer Skill Test Council: typing at 5,000 key depressions an hour (Hindi or English) for Assistant '
        'Grade-3, Registration Clerk and ASI; 8,000 in Hindi and English for Data Entry Operator; shorthand at 100 words a minute with typing at 10,000 for the '
        'stenographers; shorthand at 60 words a minute with typing at 5,000 for Steno Typist.',
        'Age: at least 21 years on 1 January 2026; the upper age and its relaxations follow the state\'s rules, with no one over 45 after all relaxations. The '
        'police posts follow the Home (Police) Department\'s own age rules and physical standards.',
        'Fee: Rs. 350 general, Rs. 250 OBC, Rs. 200 SC, ST and persons with disabilities. Candidates domiciled in Chhattisgarh who sit the exam get the fee back '
        'in the bank account it was paid from.']),
    ],
    faqs=[
      ('What is the last date to apply for CG Vyapam Group 2 2026?', '27 November 2026 (5 pm) on cgssb.cgstate.gov.in; corrections are allowed from 28 to 30 November 2026.'),
      ('When is the CG Vyapam Group 2 exam?', 'On Sunday, 10 January 2027, from 10:00 am to 12:15 pm, at the five divisional headquarters; admit cards are expected on 4 January 2027.'),
      ('How many posts are there?', '1,703, of which 1,206 are Assistant Grade-3; the rest are ASI-A (319), Registration Clerk (50), stenographers and steno typists (103) and Data Entry Operator (25).'),
      ('What is the exam pattern?', '100 objective questions for 100 marks in 2 hours: Computer 20, General Studies 20, Chhattisgarh GK 20, Mental Ability 10, Maths 10, Hindi 10 and English 10, with a quarter mark cut for each wrong answer.'),
      ('What is the application fee?', 'Rs. 350 general, Rs. 250 OBC and Rs. 200 SC, ST and persons with disabilities; refunded to Chhattisgarh domicile candidates who sit the exam.'),
      ('Where can I practise CG Vyapam previous papers?', 'On Learn with Anil: Vyapam\'s own VDAG 2021, AGDO 2021 and Stenographer 2021 general papers with its final keys, with explanations in Hindi and English.'),
    ])
ASOF_PAGE['cg-vyapam-group-2-notification-2026.html'] = '16 November 2026'

NEW['opsc-aso-notification-2026.html'] = dict(   # Anil, 15 Nov 2026: Odisha OPSC ASO (apply till 30 November); facts from OPSC's Advt. No. 15 of 2026-27 (notice and long advertisement of 5 Nov 2026), read on 16 Nov 2026
    exam='opsc-aso', board='OPSC', site='opsc.gov.in', crumb='OPSC ASO Notification 2026', faq_asof='16 November 2026',
    title='OPSC ASO Notification 2026: 340 Posts, Apply by 30 November, Exam 17 January, Age, Fee, Pattern & Previous Papers | Learn with Anil',
    desc='OPSC Assistant Section Officer (Group-B), Odisha Secretariat Service under the Home Department, Advt. No. 15 of 2026-27: 340 posts (114 for women). Apply on '
         'opsc.gov.in from 9 to 30 November 2026; written exam on 17 January 2027. Age 21–42, fee, the three-paper pattern and OPSC ASO previous papers with answers.',
    h1='OPSC ASO notification 2026: 340 posts, apply by 30 November',
    lede='The Odisha Public Service Commission (OPSC) has advertised 340 posts of Assistant Section Officer (Group-B) in the Odisha Secretariat Service cadre under '
         'the Home Department (Advt. No. 15 of 2026-27, 5 November 2026). Online applications are open on opsc.gov.in from 9 to 30 November 2026, and the written '
         'exam is on 17 January 2027. Below: the key dates, the vacancies, who can apply, the exam pattern and the OPSC ASO previous papers to practise.',
    pdf='https://www.opsc.gov.in', pdfname='OPSC Advt. No. 15 of 2026-27, opsc.gov.in > Advertisements',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. 15 of 2026-27, notice of 5 November 2026'),
        ('Online applications and fee', '9 to 30 November 2026 (5 pm) on opsc.gov.in'),
        ('Written exam', 'Sunday, 17 January 2027 (schedule and centres to be notified)'),
        ('Computer skill test', 'For candidates shortlisted from the written exam; OPSC will announce the date'),
      ]),
      ('Vacancies (340, of which 114 for women)', 'table+', (['Category', 'Posts'], [
        ('Unreserved', '144 (48 women)'), ('SEBC', '38 (13 women)'), ('SC', '81 (27 women)'), ('ST', '77 (26 women)'), ('Total', '340 (114 women)')])),
      ('', 'note', 'Within these, 25 posts are for persons with disabilities (40% or more), 19 for ex-servicemen and 3 for sports persons. Pay: Rs. 35,400 a month, '
                   'Level 9 of the ORSP Rules, 2017, with allowances.'),
      ('Exam pattern', 'table+', (['Paper', 'Subjects', 'Questions (marks) · time'], [
        ('Paper I', 'General Awareness', '100 · 1½ hours'),
        ('Paper II', '(A) Reasoning & Mental Ability 50 · (B) Mathematics (Class 10 level) 50', '100 · 1½ hours'),
        ('Paper III', '(A) English 100 · (B) Odia 100', '200 · 2 hours'),
        ('Skill test', 'Computer application (practical), qualifying: 40% needed', '50'),
      ])),
      ('', 'note', 'All written questions are multiple choice, 1 mark each, with 0.25 cut for each wrong answer. A minimum in each paper is needed (35% for UR and SEBC, '
                   '30% for SC and ST, 28% for persons with disabilities); about 1.5 times the vacancies go to the skill test, and the final merit is on the 400 written marks.'),
      ('Who can apply', 'list', [
        'A bachelor\'s degree in any discipline with adequate knowledge of computer application, and the ability to speak, read and write Odia (Odia at Middle '
        'School or Class VII level, Odia-medium Matriculation, or the Middle English School standard Odia test).',
        'Age: 21 to 42 years on 1 January 2026 (born between 2 January 1984 and 1 January 2005); 5 years more for SEBC, SC, ST, women and ex-servicemen, 10 more for '
        'persons with disabilities (15 for those also SEBC, SC or ST).',
        'Fee: Rs. 700 online; no fee for SC, ST and persons with disabilities. The fee is refunded to candidates who actually sit the written exam.']),
    ],
    faqs=[
      ('What is the last date to apply for OPSC ASO 2026?', '30 November 2026 (5 pm) on opsc.gov.in, for both the application and the fee.'),
      ('When is the OPSC ASO written exam?', 'On Sunday, 17 January 2027.'),
      ('How many posts are there in OPSC ASO 2026?', '340 Assistant Section Officer posts in the Odisha Secretariat: 144 UR, 38 SEBC, 81 SC and 77 ST, of which 114 are for women.'),
      ('What is the OPSC ASO exam pattern?', 'Three objective papers for 400 marks — General Awareness 100, Reasoning & Mathematics 100, English 100 and Odia 100 — with 0.25 cut for each wrong answer, then a qualifying 50-mark computer skill test.'),
      ('What is the age limit for OPSC ASO 2026?', '21 to 42 years on 1 January 2026, with 5 more years for SEBC, SC, ST, women and ex-servicemen and 10 more for persons with disabilities.'),
      ('Where can I practise OPSC ASO previous papers?', 'On Learn with Anil: all three papers of the 2025 and 2022 ASO exams (OPSC\'s own booklets with its keys), the Odia section in Odia.'),
    ])
ASOF_PAGE['opsc-aso-notification-2026.html'] = '16 November 2026'

NEW['osssc-medical-laboratory-technician-notification-2026.html'] = dict(   # Anil, 23 Nov 2026: OSSSC Medical Laboratory Technician PYQs; facts from OSSSC's Advertisement No. IIE-99/2026-3440/OSSSC dated 17.11.2026 (read on 23 Nov 2026)
    exam='osssc-mlt', board='OSSSC', site='osssc.gov.in', crumb='OSSSC Lab Technician Notification 2026', faq_asof='23 November 2026',
    title='OSSSC Medical Laboratory Technician Notification 2026: 380 Posts, Apply by 17 December, Exam Pattern, Age, Fee & Previous Paper | Learn with Anil',
    desc='OSSSC Advertisement No. IIE-99/2026-3440/OSSSC (17 November 2026): 380 District Cadre posts of Medical Laboratory Technician in 13 districts '
         'under the Health & Family Welfare Department. Apply on osssc.gov.in by 17 December 2026. +2 Science with DMLT/BMLT, age 21–42, pay Level 7, '
         'a 100-question written test, and the OSSSC Lab Technician previous paper with answers.',
    h1='OSSSC Medical Laboratory Technician notification 2026: 380 posts, apply by 17 December',
    lede='The Odisha Sub-ordinate Staff Selection Commission (OSSSC) has advertised 380 District Cadre Group-C posts of Medical Laboratory Technician '
         'in 13 districts under the Health & Family Welfare Department (Advertisement No. IIE-99/2026-3440/OSSSC, 17 November 2026). Register or '
         're-register on osssc.gov.in by 10 December 2026 and submit the online application by 17 December 2026. Below: the key dates, who can '
         'apply, the written test and OSSSC\'s previous Lab Technician paper to practise.',
    pdf='https://www.osssc.gov.in', pdfname='OSSSC Advertisement No. IIE-99/2026-3440/OSSSC, osssc.gov.in > Notifications',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'No. IIE-99/2026-3440/OSSSC, 17 November 2026'),
        ('Online registration / re-registration', '17 November to 10 December 2026 on osssc.gov.in'),
        ('Submission of online application', '17 November to 17 December 2026'),
        ('Written test', 'Date, time and venue to be notified on osssc.gov.in and in local newspapers'),
      ]),
      ('Post and pay', 'table+', (['Post', 'Posts', 'Pay'], [
        ('Medical Laboratory Technician (District Cadre, Group-C)', '380 in 13 districts', 'Rs. 25,500–81,100, Pay Matrix Level 7')])),
      ('Written test', 'table+', (['Part', 'Questions (marks)', 'Time'], [
        ('Diploma in Medical Laboratory Technology syllabus', '60', ''),
        ('Questions based on practical skills', '25', ''),
        ('Arithmetic (High School Certificate standard)', '10', ''),
        ('English (High School Certificate standard)', '5', ''),
        ('Total (one paper, MCQ, OMR/CBRE mode)', '100', '2 hours'),
      ])),
      ('', 'note', 'A wrong answer (or more than one answer) costs 0.25 mark; a question left blank costs nothing. The minimum qualifying score is 35%, '
                   'or 30% for SC, ST, persons with disabilities, ex-servicemen and sportspersons.'),
      ('Who can apply', 'list', [
        'Passed +2 Science (CHSE Odisha or equivalent) and a Diploma in Medical Laboratory Technology (DMLT) or Bachelor in Medical Laboratory '
        'Technology (BMLT) from a Government Medical College & Hospital of Odisha or another institution recognised by the Government of Odisha or AICTE.',
        'Registered with the Laboratory Technician Council of Odisha, with a valid registration or renewal certificate on the date of applying.',
        'Able to speak, read and write Odia (Odia at Middle School level, Odia-medium Matriculation, Odia up to Class VII, or the M.E. School standard Odia test).',
        'Age: 21 to 42 years on the date of advertisement; 5 years more for SC, ST, SEBC and women, 10 more for persons with disabilities; up to 45 for '
        'contractual Medical Laboratory Technicians under the OSH&FW Society/Scheme.',
        'Fee: Rs. 500 online; no fee for SC, ST and persons with disabilities. The fee is refunded to candidates who appear in the written test.']),
    ],
    faqs=[
      ('What is the last date to apply for OSSSC Medical Laboratory Technician 2026?', 'Registration or re-registration closes on 10 December 2026 and the online application on 17 December 2026, on osssc.gov.in.'),
      ('How many posts are there?', '380 District Cadre Group-C posts of Medical Laboratory Technician in 13 districts under the Health & Family Welfare Department.'),
      ('What is the OSSSC Lab Technician exam pattern?', 'One written test of 100 multiple-choice questions in 2 hours: DMLT syllabus 60, practical skills 25, Arithmetic 10 and English 5, with 0.25 cut for each wrong answer.'),
      ('What qualification is needed?', '+2 Science with DMLT or BMLT, registration with the Laboratory Technician Council of Odisha, and knowledge of Odia.'),
      ('Where can I practise the OSSSC Lab Technician previous paper?', 'On Learn with Anil: OSSSC\'s Laboratory Technician-2021 written test of 6 February 2022, all 100 questions with answers and explanations.'),
    ])
ASOF_PAGE['osssc-medical-laboratory-technician-notification-2026.html'] = '23 November 2026'

NEW['olm-recruitment-2026.html'] = dict(   # Anil, 23 Nov 2026: OLM / Mission Shakti PYQs; facts from OLM's advertisement (applications 6 Nov - 5 Dec 2026, missionshakti.odisha.gov.in), read on 23 Nov 2026
    exam='olm', board='OLM', site='missionshakti.odisha.gov.in', crumb='OLM Recruitment 2026', faq_asof='23 November 2026',
    title='OLM Recruitment 2026: 1,115 Posts (Block Manager, BMM, Block Accountant), Apply by 5 December, CBT Pattern, Age, Fee & PYQs | Learn with Anil',
    desc='Odisha Livelihoods Mission (OLM), Department of Mission Shakti: 1,115 contractual posts at state, district and block level. Apply on '
         'missionshakti.odisha.gov.in from 6 November to 5 December 2026. Block Manager, Block Mission Manager, Block Accountant cum MIS Assistant; '
         'age 21–42, fee Rs. 500, one 100-question CBT in English, and OLM / Mission Shakti practice questions with answers.',
    h1='OLM recruitment 2026: 1,115 posts, apply by 5 December',
    lede='The Odisha Livelihoods Mission (OLM), under the Department of Mission Shakti, Government of Odisha, is filling 1,115 contractual positions at '
         'state, district and block level, including 453 Block Managers, 174 Block Mission Managers and 247 Block Accountant cum MIS Assistants. '
         'Online applications are open on missionshakti.odisha.gov.in from 6 November to 5 December 2026 (11:55 pm). Selection is by one Computer Based '
         'Test and document verification, with no interview. Below: the key dates, the block-level posts, who can apply, the CBT pattern and practice questions.',
    pdf='https://missionshakti.odisha.gov.in', pdfname='OLM advertisement, missionshakti.odisha.gov.in',
    sections=[
      ('Key dates', 'table', [
        ('Online applications and fee', '6 November to 5 December 2026 (11:55 pm) on missionshakti.odisha.gov.in'),
        ('Computer Based Test', 'Date, shift and centre will be on the e-admit card'),
        ('After the CBT', 'Provisional answer key with objections, provisional merit list, document verification, final merit list'),
      ]),
      ('Block-level posts', 'table+', (['Post', 'Posts', 'Pay a month'], [
        ('Block Manager', '453', 'Rs. 19,080'), ('Block Mission Manager', '174', 'Rs. 31,338'), ('Block Accountant cum MIS Assistant', '247', 'Rs. 20,700')])),
      ('', 'note', 'In all, about 1,115 positions in 57 roles: about 53 at state level, 188 at district level and 874 at block level. The engagement is '
                   'contractual, first for one year, renewable on performance; it gives no right to regularisation.'),
      ('Exam pattern', 'table+', (['Paper', 'Questions', 'Time'], [
        ('Computer Based Test (English only): domain-specific syllabus of the post + common syllabus', '100 multiple-choice questions, 1 mark each', '90 minutes (120 for PwD)'),
      ])),
      ('', 'note', '0.33 mark is cut for each wrong answer; a question left blank costs nothing. There is no group discussion or interview: three candidates '
                   'per vacancy are called for document verification from the provisional merit list, and the final merit list uses the normalised CBT marks.'),
      ('Who can apply', 'list', [
        'Block Manager and Block Mission Manager: a postgraduate or master\'s degree in Arts, Science or Commerce, MBA, MSW or Rural Development, with at least 3 years of relevant experience.',
        'Block Accountant cum MIS Assistant: B.Com with PGDCA, Computer Science or IT, with at least 3 years of relevant experience.',
        'Age: 21 to 42 years on 1 January 2026; 5 years more for SC, ST, SEBC and women, 10 more for persons with disabilities. No upper age limit for candidates already working with OLM.',
        'Fee: Rs. 500 online; no fee for SC, ST and persons with disabilities. The fee is refunded to candidates who appear in the CBT.']),
    ],
    faqs=[
      ('What is the last date to apply for OLM recruitment 2026?', '5 December 2026 (11:55 pm), on missionshakti.odisha.gov.in.'),
      ('How many posts are in OLM recruitment 2026?', 'About 1,115 contractual posts, including 453 Block Managers, 174 Block Mission Managers and 247 Block Accountant cum MIS Assistants.'),
      ('What is the OLM exam pattern?', 'One Computer Based Test of 100 multiple-choice questions in 90 minutes, in English only, 1 mark each with 0.33 cut for a wrong answer, then document verification. No interview.'),
      ('When is the OLM CBT?', 'OLM has not announced the date yet; it will be on the e-admit card.'),
      ('Is this the Mission Shakti recruitment?', 'Yes. OLM works under the Department of Mission Shakti, Government of Odisha, and applications are made on the Mission Shakti website.'),
      ('Where can I practise for the OLM CBT?', 'On Learn with Anil: two sets of real exam questions on SHGs, NRLM, Mission Shakti, rural development and financial inclusion with official answers, and the Jeebika OLM mock test series in the CBT pattern.'),
    ])
ASOF_PAGE['olm-recruitment-2026.html'] = '23 November 2026'

NEW['wbpsc-ido-notification-2026.html'] = dict(   # Anil, 16 Nov 2026 ("ok continue": West Bengal IDO, apply till 26 Nov); facts from WBPSC's Advertisement No. 15/2024 (detailed advertisement and announcement of 5 Nov 2026), read on 16 Nov 2026
    exam='wbpsc-ido', board='WBPSC', site='psc.wb.gov.in', crumb='WBPSC IDO Notification 2026', faq_asof='16 November 2026',
    title='WBPSC IDO Notification 2026: 247 Posts, Apply by 26 November, Age, Fee, Exam Pattern & Previous Papers | Learn with Anil',
    desc='WBPSC Industrial Development Officer (IDO), Directorate of MSME, West Bengal, Advt. No. 15/2024: 247 posts, pay Level 10. Apply on psc.wb.gov.in from 6 to '
         '26 November 2026. Age 18–44, fee Rs. 160, the 100-mark written test pattern and WBPSC IDO previous papers with answers.',
    h1='WBPSC IDO notification 2026: 247 posts, apply by 26 November',
    lede='The West Bengal Public Service Commission (WBPSC) has advertised 247 posts of Industrial Development Officer (IDO) in the Directorate of Micro, Small & '
         'Medium Enterprises under the MSME & Textiles Department (Advertisement No. 15/2024; detailed advertisement of 5 November 2026). Online applications are '
         'open on psc.wb.gov.in from 6 to 26 November 2026; WBPSC will announce the screening test date. Below: the key dates, the vacancies, who can apply, the '
         'exam pattern and the WBPSC IDO previous papers to practise.',
    pdf='https://psc.wb.gov.in', pdfname='WBPSC Advertisement No. 15/2024, psc.wb.gov.in',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'No. 15/2024 (indicative advertisement of 24 December 2024; detailed advertisement 5 November 2026)'),
        ('Online applications', '6 to 26 November 2026 (up to 3 pm) on psc.wb.gov.in'),
        ('Last date for the fee', '26 November 2026 (up to 3 pm), online only'),
        ('Edit window', '27 November to 2 December 2026 (up to 3 pm)'),
        ('Written test (screening)', 'Date to be announced by WBPSC'),
      ]),
      ('Vacancies (247)', 'table+', (['Category', 'Posts'], [
        ('SC', '52'), ('ST', '14'), ('OBC (non-creamy layer)', '18'), ('EWS', '25'), ('Unreserved', '138'), ('Total', '247')])),
      ('', 'note', 'Within these, 9 posts are for persons with benchmark disabilities (7 unreserved, 2 SC) and 5 for meritorious sports persons. Pay: Level 10 '
                   '(Rs. 32,100 – 82,900) of the WBS (ROPA) Rules, 2019, with allowances. Reserved posts are for candidates of West Bengal only.'),
      ('Exam pattern', 'table+', (['Part', 'Subjects', 'Marks'], [
        ('Part I: written test (100 questions, 1 hour 30 minutes)', 'English 15 · Industrial Safety/Security Measures & Pollution Control 10 · Environmental Issues '
         '(Energy Conservation & Renewable Energy) 15 · Physical Science 15 · Elementary Computer Knowledge 10 · Industrial Scenario & Industrial Potential in '
         'West Bengal 15 · Mental Ability & Arithmetic 20', '100'),
        ('Part II: interview', 'Personality test (Bengali reading, writing and speaking is tested here)', '15'),
      ])),
      ('', 'note', 'All written questions are multiple choice, 1 mark each, with 0.25 cut for each wrong answer. The final merit list is on Part I and Part II '
                   'together (115 marks); the minimum aggregate is 40% for UR, EWS and MSP, 38% for OBC, 35% for SC and 30% for ST and PwBD.'),
      ('Who can apply', 'list', [
        'A degree from a recognised university, or a diploma in engineering or technology from a recognised university or institution.',
        'Age: 18 to 44 years on 1 January 2024; 5 years more for SC and ST and 3 years more for OBC (non-creamy layer) candidates of West Bengal, and up to 45 '
        'years for persons with disabilities (40% or more).',
        'Ability to read, write and speak Bengali (not required for candidates whose mother tongue is Nepali).',
        'Fee: Rs. 160 plus service charges, online only; no fee for SC and ST candidates of West Bengal and persons with benchmark disabilities.']),
    ],
    faqs=[
      ('What is the last date to apply for WBPSC IDO 2026?', '26 November 2026 (3 pm) on psc.wb.gov.in, for both the application and the fee. Applications can be edited from 27 November to 2 December 2026.'),
      ('How many posts are there in WBPSC IDO 2026?', '247 Industrial Development Officer posts in the Directorate of MSME, West Bengal: 52 SC, 14 ST, 18 OBC, 25 EWS and 138 unreserved.'),
      ('What is the WBPSC IDO exam pattern?', 'A 100-question, 100-mark written test in 1½ hours (English, Industrial Safety & Pollution Control, Environment & Energy, Physical Science, Computer, Industry in West Bengal, Mental Ability & Arithmetic) with 0.25 cut for each wrong answer, then a 15-mark interview.'),
      ('What is the age limit for WBPSC IDO?', '18 to 44 years on 1 January 2024, with 5 more years for SC and ST and 3 more for OBC candidates of West Bengal.'),
      ('When is the WBPSC IDO exam?', 'WBPSC has not announced the date yet; it says the date of the screening test will be announced.'),
      ('Where can I practise WBPSC IDO previous papers?', 'On Learn with Anil: the WBPSC IDO screening test of 2019 and the WBPSC Miscellaneous (Prelims) 2023 paper in English and Bengali, with WBPSC\'s keys and explanations.'),
    ])
ASOF_PAGE['wbpsc-ido-notification-2026.html'] = '16 November 2026'

NEW['dsssb-mts-je-notification-2026.html'] = dict(   # Anil, 16 Nov 2026 ("ok continue"); facts from DSSSB's Vacancy Notice / Advertisement No. 06/2026 of 6 Nov 2026 (Combined Examinations 2026), read on 16 Nov 2026
    exam='dsssb', board='DSSSB', site='dsssb.delhi.gov.in', crumb='DSSSB MTS & JE Notification 2026', faq_asof='16 November 2026',
    title='DSSSB MTS & JE Notification 2026: 1,260 Posts, Apply by 11 December, Age, Fee, Exam Pattern & Previous Papers | Learn with Anil',
    desc='DSSSB Advt. No. 06/2026: 1,075 Multi-Tasking Staff (MTS, MTS-Aaya, MTS General Duty) and 185 Junior Engineer (Electric/Electrical) posts in Delhi. '
         'Apply on dsssbonline.nic.in from 12 November to 11 December 2026. Age, fee, exam pattern and DSSSB previous papers with answers.',
    h1='DSSSB MTS & JE notification 2026: 1,260 posts, apply by 11 December',
    lede='The Delhi Subordinate Services Selection Board (DSSSB) has advertised 1,260 posts in its Combined Examinations, 2026 (Advertisement No. 06/2026, '
         '6 November 2026): 1,075 Multi-Tasking Staff posts (Post Code 810/26) and 185 Junior Engineer (Electric/Electrical) posts (Post Code 809/26) in '
         'departments of the Government of NCT of Delhi and its bodies. Online applications are open on dsssbonline.nic.in from 12 November to 11 December 2026. '
         'Below: the dates, posts, eligibility, exam pattern and the DSSSB previous papers to practise.',
    pdf='https://dsssb.delhi.gov.in', pdfname='DSSSB Advt. No. 06/2026, dsssb.delhi.gov.in > DSSSB Vacancies',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Vacancy Notice / Advt. No. 06/2026, Combined Examinations 2026, dated 6 November 2026'),
        ('Online applications', '12 November 2026 (12 noon) to 11 December 2026 (11:59 pm) on dsssbonline.nic.in'),
        ('Exam dates', 'To be announced on the Board\'s website'),
      ]),
      ('Posts (1,260)', 'table+', (['Post (code)', 'Departments', 'Posts', 'Pay'], [
        ('MTS (General Duty)', 'Directorate of Education', '757', 'Level 1 (Rs. 18,000 – 56,900)'),
        ('MTS – Aaya (female)', 'Directorate of Education', '239', 'Level 1'),
        ('MTS', 'Trade & Taxes 26, DUSIB 20, Weights & Measures 19, Land & Building 7, Higher Education 3, Accounts 2, Chief Electoral Officer 2', '79', 'Level 1'),
        ('Junior Engineer (Electric/Electrical), 809/26', 'Delhi Transco 75, NDMC 67, MCD 26, DUSIB 14, Agricultural Marketing Board 3', '185', 'Level 6 (Rs. 35,400 – 1,12,400); Delhi Transco Level 8'),
      ])),
      ('', 'note', 'By category, all posts: UR 537, OBC 325, SC 181, ST 94, EWS 123 (including 52 for persons with disabilities, 107 for ex-servicemen and 52 '
                   'for sportspersons). The vacancies are tentative, as reported by the departments.'),
      ('Exam pattern', 'table+', (['Exam', 'What it has', 'Questions · time'], [
        ('MTS (one tier)', 'General Awareness, General Intelligence & Reasoning, Arithmetical & Numerical Ability, Hindi, English — 40 each', '200 (200 marks) · 2 hours'),
        ('JE Tier-I', 'Section A: the same five general parts, 20 each · Section B: 100 questions on Electrical Engineering', '200 (200 marks) · 2 hours'),
        ('JE Tier-II', 'Electrical Engineering: Part I 100 one-mark questions, Part II 50 two-mark application questions', '150 (200 marks) · 2½ hours'),
      ])),
      ('', 'note', 'Wrong answers cost 0.25 mark (0.50 for a two-mark question). Questions are in Hindi and English, except the language parts. For JE, Tier-I '
                   'only shortlists candidates for Tier-II, and the final merit list is on Tier-II marks.'),
      ('Who can apply', 'list', [
        'MTS: Matriculation (Class 10) pass; age 18 to 27 years.',
        'JE: a degree or diploma in Electrical Engineering (some departments ask for 2 years\' experience with the diploma); age 18 to 27 years '
        '(18 to 32 for the NDMC posts).',
        'Age relaxation for reserved categories, persons with disabilities, ex-servicemen and Delhi government employees as given in the advertisement.',
        'Fee: Rs. 100 through SBI e-pay; no fee for women, SC, ST, persons with disabilities and ex-servicemen.']),
    ],
    faqs=[
      ('What is the last date to apply for DSSSB MTS and JE 2026?', '11 December 2026 (till 11:59 pm) on dsssbonline.nic.in. Applications opened on 12 November 2026.'),
      ('How many DSSSB MTS posts are there in 2026?', '1,075 Multi-Tasking Staff posts (Post Code 810/26), most of them in the Directorate of Education (757 MTS General Duty and 239 MTS-Aaya).'),
      ('How many DSSSB JE Electrical posts are there?', '185 Junior Engineer (Electric/Electrical) posts (Post Code 809/26) in Delhi Transco, NDMC, MCD, DUSIB and the Delhi Agricultural Marketing Board.'),
      ('What is the DSSSB MTS exam pattern?', 'One 2-hour test of 200 questions for 200 marks: General Awareness, Reasoning, Arithmetic, Hindi and English, 40 each, with 0.25 cut for each wrong answer.'),
      ('What is the age limit for DSSSB MTS 2026?', '18 to 27 years, with relaxation for reserved categories as per the advertisement.'),
      ('Where can I practise DSSSB previous papers?', 'On Learn with Anil: the DSSSB JE (Electrical) and Patwari papers of 2022 with DSSSB\'s own answers, in Hindi and English with explanations.'),
    ])
ASOF_PAGE['dsssb-mts-je-notification-2026.html'] = '16 November 2026'

NEW['jkssb-je-civil-notification-2026.html'] = dict(   # Anil, 16 Nov 2026 ("JKSSB JE Civil ... do it"); facts from JKSSB Advertisement Notification No. 11 of 2026 (27 Oct 2026), read on 16 Nov 2026
    exam='jkssb-je-civil', board='JKSSB', site='jkssb.nic.in', crumb='JKSSB JE Civil Notification 2026', faq_asof='16 November 2026',
    title='JKSSB JE Civil Notification 2026: 458 Posts, Apply 30 November – 29 December, Age, Fee, Exam & Previous Papers | Learn with Anil',
    desc='JKSSB Advertisement Notification No. 11 of 2026: 458 Junior Engineer (Civil) posts in the Jal Shakti (282) and PWD (R&B) (176) departments, Level-6. '
         'Apply on jkssb.nic.in from 30 November to 29 December 2026. Age, fee, qualification, exam scheme and JKSSB JE Civil previous papers with answers.',
    h1='JKSSB JE Civil notification 2026: 458 posts, apply 30 November – 29 December',
    lede='The Jammu & Kashmir Services Selection Board (JKSSB) has advertised 458 posts of Junior Engineer (Civil), UT cadre, in the Jal Shakti Department '
         '(282) and the Public Works (R&B) Department (176) (Advertisement Notification No. 11 of 2026, 27 October 2026). Online applications are open on '
         'jkssb.nic.in from 30 November to 29 December 2026. Below: the dates, vacancies, eligibility, exam scheme and the JKSSB JE Civil previous papers to practise.',
    pdf='https://jkssb.nic.in', pdfname='JKSSB Advertisement Notification No. 11 of 2026, jkssb.nic.in > Advertisement',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Notification No. 11 of 2026, dated 27 October 2026'),
        ('Online applications', '30 November to 29 December 2026 on jkssb.nic.in'),
        ('Written exam', 'Date and centres to be notified separately by JKSSB'),
      ]),
      ('Vacancies (458)', 'table+', (['Department', 'OM', 'SC', 'ST-1', 'ST-2', 'OBC', 'ALC/IB', 'RBA', 'EWS', 'Total'], [
        ('Jal Shakti (Item 266)', '113', '23', '28', '28', '22', '11', '28', '29', '282'),
        ('PWD (R&B) (Item 267)', '71', '14', '18', '18', '14', '7', '17', '17', '176'),
        ('Total', '184', '37', '46', '46', '36', '18', '45', '46', '458')])),
      ('', 'note', 'Pay: Level-6 (Rs. 35,400 – 1,12,400). Horizontal reservation for ex-servicemen and persons with benchmark disabilities as per the rules.'),
      ('Exam scheme', 'list', [
        'An objective, multiple-choice written (OMR) exam in English only, with one-fourth of the marks cut for each wrong answer.',
        'Selection is on merit in the written exam, followed by document verification.',
        'JKSSB will notify the syllabus separately. The 2025 and 2023 JE (Civil) papers had 120 Civil Engineering questions in 120 minutes.']),
      ('Who can apply', 'list', [
        'Domicile of the Union Territory of Jammu & Kashmir (certificate on or before 29 December 2026).',
        'A 3-year Diploma in Civil Engineering from a government-recognised institute, or a degree in Civil Engineering, or AMIE Sections A and B.',
        'Age on 1 January 2026: 40 years at most for Open Merit; 43 for SC, ST-1, ST-2, RBA, ALC/IB, EWS and OBC; 42 for physically challenged persons; '
        'candidates must not be born after 1 January 2008.',
        'Fee: Rs. 600 online (Rs. 500 for SC, ST-1, ST-2, EWS and PwBD candidates).']),
    ],
    faqs=[
      ('What is the last date to apply for JKSSB JE Civil 2026?', '29 December 2026. Online applications on jkssb.nic.in open on 30 November 2026.'),
      ('How many JKSSB JE Civil posts are there?', '458: 282 in the Jal Shakti Department and 176 in the Public Works (R&B) Department.'),
      ('What is the JKSSB JE Civil exam pattern?', 'An objective (OMR) written test in English with negative marking of one-fourth for each wrong answer; selection is on merit in the written exam. Past papers had 120 questions in 120 minutes.'),
      ('What is the age limit for JKSSB JE Civil?', 'On 1 January 2026, at most 40 years for Open Merit and 43 for SC, ST, RBA, ALC/IB, EWS and OBC candidates (42 for physically challenged persons).'),
      ('What is the fee for JKSSB JE Civil?', 'Rs. 600, or Rs. 500 for SC, ST-1, ST-2, EWS and PwBD candidates, paid online.'),
      ('Where can I practise JKSSB JE Civil previous papers?', 'On Learn with Anil: the JKSSB JE (Civil) papers of 2025 and 2023, JKSSB\'s own booklets with its final keys and explanations.'),
    ])
ASOF_PAGE['jkssb-je-civil-notification-2026.html'] = '16 November 2026'

NEW['meghalaya-psc-notification-2026.html'] = dict(   # Anil, 16 Nov 2026 ("Meghalaya PSC ... do it"); facts from MPSC Advt. No. 01/2026-2027 of 12 Nov 2026 (mpsc.meghalaya.gov.in), read on 16 Nov 2026
    exam='meghalaya-psc', board='Meghalaya PSC', site='mpsc.meghalaya.gov.in', crumb='Meghalaya PSC Notification 2026', faq_asof='16 November 2026',
    title='Meghalaya PSC Notification 2026 (Advt. 01/2026-27): 20 Posts, Apply by 12 December, Age, Fee, Screening Test & Previous Papers | Learn with Anil',
    desc='Meghalaya PSC Advt. No. 01/2026-2027: 20 posts — Assistant Engineer (Mechanical), Assistant Research Officer (Finance), Junior Athletic and Archery '
         'Coaches, Journalist. Apply online by 5 pm on 12 December 2026. Age, fee, screening test pattern and Meghalaya PSC previous papers with answers.',
    h1='Meghalaya PSC notification 2026: 20 posts, apply by 12 December',
    lede='The Meghalaya Public Service Commission (MPSC) has advertised 20 posts in five departments (Advt. No. 01/2026-2027, 12 November 2026). Online '
         'applications are open till 5 pm on 12 December 2026. Selection is by an MCQ screening test and a personal interview. Below: the posts, '
         'eligibility, fee, the screening test for each post and the Meghalaya PSC previous papers to practise.',
    pdf='https://mpsc.meghalaya.gov.in/advertisements.html', pdfname='MPSC Advt. No. 01/2026-2027, mpsc.meghalaya.gov.in > Advertisements',
    sections=[
      ('Key dates', 'table', [
        ('Advertisement', 'Advt. No. 01/2026-2027, dated 12 November 2026'),
        ('Last date to apply online', '12 December 2026, 5 pm'),
        ('Screening test and interview', 'Dates to be notified by MPSC; exam centres at Shillong, Tura, Jowai, Williamnagar and Nongstoin'),
      ]),
      ('Posts (20)', 'table+', (['Post', 'Department', 'Posts', 'Pay'], [
        ('Assistant Engineer (Mechanical), Group A', 'PWD (R&B)', '4', 'Level 15'),
        ('Assistant Research Officer', 'Finance (Economic Affairs)', '5', 'Level 15'),
        ('Junior Athletic Coach', 'Sports & Youth Affairs', '2', 'Level 11'),
        ('Junior Archery Coach', 'Sports & Youth Affairs', '1', 'Level 11'),
        ('Journalist', 'Information & Public Relations', '8', 'Level 8'),
      ])),
      ('Screening test (MCQ)', 'table+', (['Post', 'Parts', 'Marks'], [
        ('AE (Mechanical)', 'General English 50 · GK & Current Affairs 60 · Aptitude & Reasoning 20 · Mechanical Engineering (degree level) 170', '300'),
        ('Assistant Research Officer', 'General English 50 · GK & Current Affairs 50 · Basic Computer, Aptitude & Reasoning 30 · Economics/Statistics/Maths/Commerce 170', '300'),
        ('Junior Athletic / Archery Coach', 'General English 50 · GK & Current Affairs 100 · Reasoning 50 (Class XII level)', '200'),
        ('Journalist', 'General English 50 · GK & Current Affairs 50 · Basic Computer, Aptitude & Reasoning 30 · Mass Communication/Journalism 170', '300'),
      ])),
      ('', 'note', 'Candidates who pass the screening test are called for a personal interview with their original documents.'),
      ('Who can apply', 'list', [
        'Qualification as listed for each post (for example, B.E. Mechanical for AE; a master\'s in Economics/Statistics/Commerce/Mathematics for ARO; a '
        'degree with a diploma or degree in mass communication/journalism for Journalist; sports-coaching qualifications for the coaches).',
        'Age on 1 January 2026: 21 to 32 years for AE (Mechanical); 18 to 32 for the other posts; 5 more years for SC/ST candidates with a Meghalaya '
        'certificate.',
        'Fee: Rs. 460 (AE, ARO), Rs. 350 (coaches), Rs. 320 (Journalist); half for SC/ST permanent residents of Meghalaya; persons with disabilities exempt.']),
    ],
    faqs=[
      ('What is the last date to apply for Meghalaya PSC Advt. 01/2026-2027?', '12 December 2026, 5 pm, online on the MPSC website.'),
      ('How many posts are in Meghalaya PSC Advt. 01/2026-2027?', '20: Assistant Engineer (Mechanical) 4, Assistant Research Officer 5, Junior Athletic Coach 2, Junior Archery Coach 1 and Journalist 8.'),
      ('What is the Meghalaya PSC screening test pattern?', 'MCQ papers with General English, General Knowledge & Current Affairs and Aptitude/Reasoning (plus a subject part for AE, ARO and Journalist), followed by a personal interview.'),
      ('What is the age limit?', 'On 1 January 2026, 21–32 years for AE (Mechanical) and 18–32 for the other posts, with 5 years\' relaxation for SC/ST candidates of Meghalaya.'),
      ('Where can I practise Meghalaya PSC previous papers?', 'On Learn with Anil: MCS Prelims 2026 Papers I and II and the LDA screening test 2026, MPSC\'s own booklets with its answer keys and explanations.'),
    ])
ASOF_PAGE['meghalaya-psc-notification-2026.html'] = '16 November 2026'


# ---- 16 Nov 2026 (Anil: "why mistake book and notification is not present in every exam tile"): pages for the six exams that had no notification card.
# Facts read on 16 Nov 2026 from news and coaching pages that quote the official notices (sources named on each page); re-check before big changes.

NEW['upsc-ifos-2027-notification.html'] = dict(
    exam=None, ename='UPSC IFoS',   # the IFoS hub is not an app exam (tools/upscmains.py), so no exam id here
    board='UPSC', site='upsc.gov.in', crumb='IFoS 2026 Mains & 2027 Notification', faq_asof='16 November 2026',
    title='UPSC IFoS 2026 Mains (22–29 November) & IFoS 2027 Notification on 13 January: Vacancies, Eligibility, Pattern | Learn with Anil',
    desc='UPSC Indian Forest Service: the IFoS 2026 Main exam runs from 22 to 29 November 2026 (about 80 vacancies). IFoS 2027 will be notified with the Civil '
         'Services on 13 January 2027; Prelims on 23 May 2027, Mains from 21 November 2027. Eligibility, age, the Mains pattern and IFoS previous papers.',
    h1='UPSC IFoS: 2026 Mains from 22 November, 2027 notification on 13 January',
    lede='The Indian Forest Service (IFoS) Main Examination 2026 is from 22 to 29 November 2026, with General English and General Knowledge on the first day. '
         'The next cycle, IFoS 2027, will be notified together with the Civil Services on 13 January 2027 (apply by 2 February), with the common Prelims on '
         '23 May 2027. Below: the dates, vacancies, who can apply, the Mains pattern and the IFoS previous papers to practise.',
    hi='यूपीएससी भारतीय वन सेवा: मुख्य परीक्षा 2026 — 22 से 29 नवंबर; IFoS 2027 की अधिसूचना 13 जनवरी 2027 को, प्रारंभिक परीक्षा 23 मई 2027 (सिविल सेवा के साथ)।',
    pdf='https://upsc.gov.in', pdfname='UPSC: Indian Forest Service Examination Notice No. 06/2026-IFoSE, IFoS (Main) 2026 time-table and the UPSC Calendar 2027 (upsc.gov.in)',
    related=['upsc-cse-2027-notification.html'],
    sections=[
      ('IFoS 2026: where it stands', 'table', [
        ('Notification', 'Examination Notice No. 06/2026-IFoSE, 4 February 2026 (applications closed 27 February 2026)'),
        ('Preliminary exam', '24 May 2026, through the Civil Services (Preliminary) Examination'),
        ('Main exam', '22 to 29 November 2026, two sessions a day (9 am–12 noon and 2:30–5:30 pm); no paper on 24 November'),
        ('First day (22 November)', 'Paper I General English (forenoon) and Paper II General Knowledge (afternoon); the optional papers follow from 23 November'),
        ('e-Admit cards', 'Out on upsconline.nic.in'),
        ('Then', 'Interview (personality test) for those who clear the Mains, then the final result'),
      ]),
      ('IFoS 2026 vacancies: about 80', 'table+', (['Category', 'Posts'], [
        ('Unreserved', '33'), ('OBC', '21'), ('SC', '12'), ('EWS', '8'), ('ST', '6'), ('Total', 'about 80')])),
      ('IFoS 2027: expected dates (UPSC Calendar 2027)', 'table', [
        ('Notification (with Civil Services 2027)', '13 January 2027'), ('Last date to apply', '2 February 2027'),
        ('Preliminary exam (common with CSE)', 'Sunday, 23 May 2027'), ('Main exam', 'From Sunday, 21 November 2027 (7 days)'),
        ('Vacancies', 'Will be given in the 2027 notification'),
      ]),
      ('Who can apply', 'list', [
        'A bachelor\'s degree with at least one of Animal Husbandry & Veterinary Science, Botany, Chemistry, Geology, Mathematics, Physics, Statistics or Zoology, '
        'or a bachelor\'s degree in Agriculture, Forestry or Engineering.',
        'Age 21 to 32 years on 1 August of the exam year, with the usual relaxations (5 years for SC and ST, 3 for OBC, 10 for persons with benchmark disabilities).',
        'One online form covers both the Civil Services and IFoS Prelims; tick IFoS in it. Fee Rs. 100, no fee for women, SC, ST and persons with benchmark disabilities.']),
      ('Main exam pattern (1,400 marks + 300 interview)', 'table+', (['Paper', 'Marks'], [
        ('Paper I: General English (essay, précis, comprehension, grammar)', '300'), ('Paper II: General Knowledge', '300'),
        ('Papers III–VI: two optional subjects, two papers each', '4 × 200 = 800'), ('Personality test (interview)', '300')])),
      ('', 'note', 'IFoS has its own Prelims cut-off, usually higher than the Civil Services cut-off, though the two papers are the same. Optional subjects include '
                   'Forestry, Botany, Zoology, Agriculture, Geology, Physics, Chemistry, Mathematics, Statistics and the engineering subjects; some pairs cannot be taken together.'),
    ],
    tail_html='<h2>Practise the IFoS previous papers</h2><p>Learn with Anil has the IFoS Mains Paper I (General English) and Paper II (General Knowledge) '
              'from UPSC\'s official papers, 2019–2025, each question with a model answer, and the common Civil Services Prelims papers with answer keys and '
              'explanations in English and Hindi.</p><p><a href="/upsc-ifos/">UPSC IFoS home</a> · <a href="/upsc-ifos/mains-pyqs/">IFoS Mains PYQs with model answers</a> · '
              '<a href="/upsc-prelims/pyqs.html">Prelims previous papers</a></p>',
    faqs=[
      ('When is the UPSC IFoS Mains 2026?', 'From 22 to 29 November 2026. General English and General Knowledge are on 22 November; the optional papers follow (no paper on 24 November).'),
      ('When will the IFoS 2027 notification come?', 'On 13 January 2027, together with the Civil Services 2027 notification, as per the UPSC Calendar 2027. The last date to apply is 2 February 2027.'),
      ('When is the IFoS Prelims 2027?', 'On Sunday, 23 May 2027. It is the same paper as the Civil Services Prelims; IFoS has its own cut-off.'),
      ('How many IFoS vacancies are there in 2026?', 'About 80: 33 unreserved, 21 OBC, 12 SC, 8 EWS and 6 ST, as given in UPSC\'s notice.'),
      ('What is the age limit for IFoS?', '21 to 32 years on 1 August of the exam year, with relaxation for SC, ST, OBC and persons with benchmark disabilities.'),
      ('Where can I practise IFoS Mains previous questions?', 'On Learn with Anil: Paper I General English and Paper II General Knowledge, 2019–2025, with model answers.'),
    ])
ASOF_PAGE['upsc-ifos-2027-notification.html'] = '16 November 2026'

NEW['appsc-aso-notification-2026.html'] = dict(
    exam='appsc-aso', board='APPSC', site='psc.ap.gov.in', crumb='APPSC ASO Notification 2026', faq_asof='16 November 2026',
    title='APPSC ASO Notification 2026: 196 Assistant Statistical Officer Posts, Last Date 12 November, Exam Pattern, Age 44 & Previous Papers | Learn with Anil',
    desc='APPSC Notification No. 20/2026: 196 Assistant Statistical Officer posts in the A.P. Economics & Statistical Subordinate Service. Applications closed on '
         '12 November 2026 (extended from 2 November); the exam date is awaited. Degree with Statistics, age 18–44, the two-paper CBRT pattern and ASO previous papers.',
    h1='APPSC ASO notification 2026: 196 Assistant Statistical Officer posts',
    lede='The Andhra Pradesh Public Service Commission (APPSC) has notified 196 posts of Assistant Statistical Officer (ASO) in the A.P. Economics & Statistical '
         'Subordinate Service (Notification No. 20/2026). Online applications ran from 13 October to 12 November 2026 (the last date was extended from 2 November); '
         'APPSC will announce the exam date. Below: the dates, who could apply, the exam pattern and the ASO previous papers to practise.',
    te='ఏపీపీఎస్సీ అసిస్టెంట్ స్టాటిస్టికల్ ఆఫీసర్ నోటిఫికేషన్ (నం. 20/2026): 196 పోస్టులు. దరఖాస్తు గడువు నవంబర్ 12, 2026తో ముగిసింది; పరీక్ష తేదీ ఇంకా ప్రకటించలేదు. '
       'పేపర్-1 జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ, పేపర్-2 ఎకనామిక్స్, అకౌంటింగ్, కంప్యూటర్స్ & స్టాటిస్టిక్స్.',
    pdf='https://psc.ap.gov.in', pdfname='APPSC Notification No. 20/2026 (Assistant Statistical Officer, A.P. Economics & Statistical Subordinate Service), psc.ap.gov.in',
    related=['tgpsc-mpso-aso-notification-2026.html'],
    sections=[
      ('Key dates', 'table', [
        ('Notification', 'No. 20/2026 (brief notice 15 September 2026; detailed notification with the online application from 13 October 2026)'),
        ('Online applications', '13 October to 12 November 2026, 11:59 pm (extended from 2 November); now closed'),
        ('Written exam (CBRT)', 'Date to be announced by APPSC; there is no screening test'),
        ('Computer Proficiency Test', 'For candidates who qualify in the written exam'),
      ]),
      ('Posts and pay', 'table', [
        ('Post', 'Assistant Statistical Officer, A.P. Economics & Statistical Subordinate Service'), ('Vacancies', '196 (provisional)'),
        ('Pay', 'Rs. 37,640 – 1,15,500 (RPS 2022), with allowances')]),
      ('Exam pattern (single level, online CBRT, degree standard)', 'table+', (['Paper', 'Subject', 'Questions · minutes · marks'], [
        ('Paper I', 'General Studies & Mental Ability', '150 · 150 · 150'),
        ('Paper II', 'Economics, Financial Accounting, Basics of Computers and Statistics', '150 · 150 · 150'),
        ('CPT', 'Computer Proficiency Test: fundamentals (20%) and word processing, spreadsheet and presentation practicals (80%); qualifying', '—')])),
      ('', 'note', 'The written exam is 300 marks; one-third of a mark is cut for each wrong answer. Marks may be normalised if the exam is held in more than one session. '
                   'The CPT only has to be passed: 40% for OC, 35% for BC and 30% for SC, ST and persons with disabilities.'),
      ('Who could apply', 'list', [
        'A bachelor\'s degree with Statistics as a main subject, or with Mathematics, Economics, Commerce or Computer Science as a main subject and Statistics '
        'studied as a paper.',
        'Age 18 to 44 years on 1 July 2026 (the upper limit was raised from 42 to 44 by G.O.Ms.No.187 of 14 September 2026); 5 years more for SC, ST, BC and EWS, '
        '10 more for persons with disabilities.',
        'Fee: Rs. 250 application fee plus Rs. 80 exam fee; the exam fee is waived for SC, ST, BC, persons with disabilities, ex-servicemen, white-card families '
        'and unemployed youth as defined in the notification.']),
    ],
    faqs=[
      ('What is the last date to apply for APPSC ASO 2026?', 'It was 12 November 2026 (extended from 2 November). Applications are now closed.'),
      ('When is the APPSC ASO exam 2026?', 'APPSC has not announced the date yet. It will be a single online (CBRT) exam with no screening test; watch psc.ap.gov.in for the date and hall tickets.'),
      ('How many posts are there in APPSC ASO 2026?', '196 Assistant Statistical Officer posts in the A.P. Economics & Statistical Subordinate Service (provisional).'),
      ('What is the APPSC ASO exam pattern?', 'Paper I General Studies & Mental Ability and Paper II Economics, Accounting, Computers and Statistics, 150 questions and 150 marks each, then a qualifying Computer Proficiency Test.'),
      ('What is the age limit for APPSC ASO 2026?', '18 to 44 years on 1 July 2026, with 5 more years for SC, ST, BC and EWS and 10 more for persons with disabilities.'),
      ('Where can I practise APPSC ASO previous papers?', 'On Learn with Anil: the Paper II (Statistics) papers of the 2025 and 2022 ASO exams with APPSC\'s final keys and explanations in English and Telugu.'),
    ])
ASOF_PAGE['appsc-aso-notification-2026.html'] = '16 November 2026'

_TG1_FAQ_STATUS = 'No. As of 16 November 2026 TGPSC has not issued a new Group-I notification. The last one was Notification No. 02/2024 (563 posts), whose selection list came in September 2025.'
NEW['tgpsc-group-1-notification-2026.html'] = dict(
    exam='tgpsc-group-1', board='TGPSC', site='tgpsc.gov.in', crumb='TGPSC Group-I Notification', faq_asof='16 November 2026',
    title='TGPSC Group 1 Notification 2026: Latest Status, 2024 Recruitment (563 Posts) Timeline, Exam Pattern & Previous Papers | Learn with Anil',
    desc='Is there a new TGPSC Group-I notification? Not yet (16 November 2026). The last recruitment, Notification 02/2024 for 563 posts: Prelims 9 June 2024, '
         'Mains 21–27 October 2024, 562 selected; the High Court and the Supreme Court upheld it in 2026. Prelims and Mains pattern and Group-I previous papers.',
    h1='TGPSC Group-I notification 2026: latest status',
    lede='As of 16 November 2026, the Telangana Public Service Commission (TGPSC) has not issued a new Group-I notification. The last recruitment, under '
         'Notification No. 02/2024 for 563 posts, is complete: 562 candidates were selected, and the courts upheld the result in 2026. Below: that timeline, the '
         'Prelims and Mains pattern, and the Group-I previous papers to start with while the next notification is awaited.',
    te='టీజీపీఎస్సీ గ్రూప్-1: 16 నవంబర్ 2026 నాటికి కొత్త నోటిఫికేషన్ రాలేదు. చివరి నోటిఫికేషన్ 02/2024 (563 పోస్టులు) — ప్రిలిమ్స్ 9 జూన్ 2024, '
       'మెయిన్స్ అక్టోబర్ 2024, 562 మంది ఎంపిక. పరీక్ష విధానం, గత ప్రశ్నపత్రాలు ఇక్కడ.',
    pdf='https://www.tgpsc.gov.in', pdfname='TGPSC Notification No. 02/2024 (Group-I Services) and its results, tgpsc.gov.in',
    related=['tgpsc-group-2-notification-2026.html', 'tgpsc-mpso-aso-notification-2026.html'],
    sections=[
      ('Status', 'table', [
        ('New Group-I notification', 'Not issued yet (checked 16 November 2026). It will appear on tgpsc.gov.in; ignore notices shared only on social media.'),
        ('Last notification', 'No. 02/2024, 19 February 2024, 563 posts (Deputy Collector, DSP, Commercial Tax Officer, District Registrar and others)'),
      ]),
      ('How the 2024 recruitment went', 'table', [
        ('Prelims', '9 June 2024 (31,382 qualified for the Mains at 1:50)'), ('Mains', '21 to 27 October 2024 (about 30,000 wrote)'),
        ('General Ranking List', '30 March 2025'),
        ('Selection list', 'September 2025: 562 provisionally selected, one post withheld because of a court case'),
        ('Court cases', 'A single judge set the Mains result aside on 9 September 2025; a division bench of the High Court upheld it on 5 February 2026, '
                        'and the Supreme Court rejected the plea against it in April 2026'),
      ]),
      ('Exam pattern (as in Notification 02/2024)', 'table+', (['Stage', 'Papers', 'Marks'], [
        ('Prelims (screening)', 'General Studies & Mental Ability, 150 questions, 2½ hours, objective', '150 (not counted in the final merit)'),
        ('Mains (written, descriptive)', 'General English (qualifying) and six papers of 3 hours each: I General Essay; II History, Culture & Geography; '
                                         'III Indian Society, Constitution & Governance; IV Economy & Development; V Science & Technology and Data Interpretation; '
                                         'VI Telangana Movement & State Formation', '6 × 150 = 900'),
      ])),
      ('', 'note', 'There is no interview: the final selection is on the 900 Mains marks. The Mains papers can be written in English, Telugu or Urdu.'),
    ],
    faqs=[
      ('Is there a TGPSC Group-I notification in 2026?', _TG1_FAQ_STATUS),
      ('How many posts were there in the last TGPSC Group-I?', '563 posts under Notification No. 02/2024; 562 candidates were selected and one post was withheld because of a court case.'),
      ('Is there an interview in TGPSC Group-I?', 'No. Selection is on the Mains written marks (six papers of 150 marks); the Prelims only screens candidates for the Mains.'),
      ('What is the TGPSC Group-I Prelims pattern?', 'One objective paper of General Studies & Mental Ability: 150 questions, 150 marks, 2½ hours.'),
      ('Where can I practise TGPSC Group-I previous papers?', 'On Learn with Anil: the 2024, 2023 and 2022 Prelims papers with TGPSC\'s final keys and explanations in English and Telugu, and the 2024 Mains questions.'),
    ])
ASOF_PAGE['tgpsc-group-1-notification-2026.html'] = '16 November 2026'

NEW['tgpsc-group-2-notification-2026.html'] = dict(
    exam='tgpsc-group-2', board='TGPSC', site='tgpsc.gov.in', crumb='TGPSC Group-II Notification', faq_asof='16 November 2026',
    title='TGPSC Group 2 Notification 2026: Latest Status, 783-Post Recruitment (28/2022) Timeline, Exam Pattern & Previous Papers | Learn with Anil',
    desc='Is there a new TGPSC Group-II notification? Not yet (16 November 2026); posts of a "2026 notification for 783 posts" are the old 2022 one. Notification '
         '28/2022: exam 15–16 December 2024, 782 selected on 28 September 2025. The four-paper pattern and Group-II previous papers with answers.',
    h1='TGPSC Group-II notification 2026: latest status',
    lede='As of 16 November 2026, TGPSC has not issued a new Group-II notification. Job sites that show a "Group-2 2026 notification for 783 posts" are repeating '
         'the 2022 notification, whose recruitment is complete: 782 candidates were selected on 28 September 2025. Below: that timeline, the exam pattern and the '
         'Group-II previous papers to start with.',
    te='టీజీపీఎస్సీ గ్రూప్-2: 16 నవంబర్ 2026 నాటికి కొత్త నోటిఫికేషన్ రాలేదు. చివరి నోటిఫికేషన్ 28/2022 (783 పోస్టులు) — పరీక్ష డిసెంబర్ 2024లో, '
       '782 మంది ఎంపిక (సెప్టెంబర్ 28, 2025). పరీక్ష విధానం, గత ప్రశ్నపత్రాలు ఇక్కడ.',
    pdf='https://www.tgpsc.gov.in', pdfname='TGPSC Notification No. 28/2022 (Group-II Services) and its results, tgpsc.gov.in',
    related=['tgpsc-group-1-notification-2026.html', 'tgpsc-mpso-aso-notification-2026.html'],
    sections=[
      ('Status', 'table', [
        ('New Group-II notification', 'Not issued yet (checked 16 November 2026). Trust only tgpsc.gov.in; "2026" posts with 783 posts are the 2022 notification.'),
        ('Last notification', 'No. 28/2022, 29 December 2022: 783 posts in 18 post codes (Municipal Commissioner Gr. III, Assistant Commercial Tax Officer, '
                              'Sub-Registrar, Mandal Revenue Officer posts and others)'),
      ]),
      ('How the 28/2022 recruitment went', 'table', [
        ('Applications', '18 January to 16 February 2023 (about 5.5 lakh applied)'), ('Written exam', '15 and 16 December 2024 (after several postponements)'),
        ('General Ranking List', '11 March 2025'), ('Selection list', '28 September 2025: 782 provisionally selected, one post withheld'),
      ]),
      ('Exam pattern (objective, no interview)', 'table+', (['Paper', 'Subject', 'Questions · marks · time'], [
        ('Paper I', 'General Studies & General Abilities', '150 · 150 · 2½ hours'), ('Paper II', 'History, Polity & Society', '150 · 150 · 2½ hours'),
        ('Paper III', 'Economy & Development', '150 · 150 · 2½ hours'), ('Paper IV', 'Telangana Movement & State Formation', '150 · 150 · 2½ hours'),
        ('Total', '', '600 marks')])),
      ('', 'note', 'Selection is on the 600 written marks; there is no interview. The papers are bilingual (English and Telugu), with Urdu on request.'),
    ],
    faqs=[
      ('Is there a TGPSC Group-II notification in 2026?', 'No. As of 16 November 2026 TGPSC has not issued one. The last was Notification No. 28/2022 for 783 posts, completed in September 2025.'),
      ('Is the "TGPSC Group 2 2026 notification for 783 posts" real?', 'No. 783 posts is the 2022 notification (No. 28/2022), whose exam was in December 2024 and selection list in September 2025.'),
      ('How many were selected in TGPSC Group-II 2024?', '782 against 783 posts; one post was withheld. The list came on 28 September 2025.'),
      ('What is the TGPSC Group-II exam pattern?', 'Four objective papers of 150 questions and 150 marks each (600 marks): GS & General Abilities; History, Polity & Society; Economy & Development; Telangana Movement. No interview.'),
      ('Where can I practise TGPSC Group-II previous papers?', 'On Learn with Anil: all four papers of the December 2024 exam with TGPSC\'s final key and explanations in English and Telugu.'),
    ])
ASOF_PAGE['tgpsc-group-2-notification-2026.html'] = '16 November 2026'

NEW['sbi-po-2026-notification.html'] = dict(
    exam='sbi-po', board='SBI', site='sbi.bank.in', crumb='SBI PO 2026', faq_asof='16 November 2026',
    title='SBI PO 2026: 1,500 Posts, Mains Result Out, Group Exercise & Interview from 18 November, Final Result, Pattern & Mock Tests | Learn with Anil',
    desc='SBI PO 2026 (CRPD/PO/2026-27/09): 1,500 Probationary Officer posts. Prelims 1–2 August, Mains 12 September; 4,367 shortlisted for Phase III — psychometric '
         'test 31 October, group exercise and interviews from 18 November 2026. Vacancies, final merit, the Prelims pattern and free-pattern mock tests.',
    h1='SBI PO 2026: group exercise and interviews from 18 November',
    lede='The State Bank of India is recruiting 1,500 Probationary Officers (Advertisement CRPD/PO/2026-27/09). The Prelims and Mains are over; the Mains result '
         'shortlisted 4,367 candidates for Phase III. The psychometric test was held on 31 October and the group exercise and interviews start on 18 November 2026 '
         '(tentative), with the final result expected in November–December. Below: the dates, vacancies, how the final merit works and the exam pattern.',
    hi='एसबीआई पीओ 2026 (विज्ञापन CRPD/PO/2026-27/09): 1,500 पद। मेन्स का परिणाम आ चुका है; ग्रुप एक्सरसाइज़ और इंटरव्यू 18 नवंबर 2026 से (संभावित)।',
    pdf='https://sbi.bank.in/web/careers/current-openings', pdfname='SBI Advertisement No. CRPD/PO/2026-27/09 and its notices, sbi.bank.in > Careers',
    related=['ibps-so-2026-notification.html'],
    sections=[
      ('Key dates', 'table', [
        ('Notification', '18 June 2026 (CRPD/PO/2026-27/09)'), ('Online applications', '18 June to 8 July 2026 (closed)'),
        ('Phase I: Prelims', '1 and 2 August 2026 (result at the end of August)'), ('Phase II: Mains', '12 September 2026 (result in mid-October; 4,367 shortlisted)'),
        ('Phase III: psychometric test', '31 October 2026'), ('Phase III: group exercise and interview', 'From 18 November 2026 (tentative)'),
        ('Final result', 'November–December 2026 (tentative)'),
      ]),
      ('Vacancies: 1,500', 'table+', (['Category', 'Regular', 'Backlog'], [
        ('UR', '588', '—'), ('OBC', '390', '—'), ('SC', '216', '18'), ('ST', '108', '36'), ('EWS', '144', '—'), ('Total', '1,446', '54')])),
      ('How the final merit is made', 'list', [
        'Prelims marks do not count; the Prelims only shortlists for the Mains.',
        'Mains (objective + descriptive) marks are converted to 75, and Phase III (group exercise 20 + interview 30 = 50) to 25: final merit out of 100.']),
      ('Prelims pattern (Phase I)', 'table+', (['Section', 'Questions (marks)', 'Time'], [
        ('English Language', '40', '20 minutes'), ('Quantitative Aptitude', '30', '20 minutes'), ('Reasoning Ability', '30', '20 minutes'),
        ('Total', '100', '1 hour')])),
      ('', 'note', 'A quarter of the marks for a question is cut for each wrong answer. Who could apply: graduates in any discipline, aged 21 to 30 on 1 April 2026 '
                   '(born 2 April 1996 to 1 April 2005), with the usual relaxations.'),
    ],
    faqs=[
      ('When is the SBI PO 2026 interview?', 'The group exercise and interviews start on 18 November 2026 (tentative); each candidate\'s date is on the Phase III call letter on sbi.bank.in.'),
      ('How many candidates cleared the SBI PO 2026 Mains?', '4,367 candidates were shortlisted for Phase III (psychometric test, group exercise and interview) for 1,500 posts.'),
      ('When will the SBI PO 2026 final result come?', 'SBI\'s tentative schedule puts it in November–December 2026, after the interviews.'),
      ('How many vacancies are there in SBI PO 2026?', '1,500: 1,446 regular (588 UR, 390 OBC, 216 SC, 108 ST, 144 EWS) and 54 backlog (18 SC, 36 ST).'),
      ('How is the SBI PO final merit calculated?', 'Mains marks out of 75 plus group exercise and interview out of 25. Prelims marks are not counted.'),
      ('Are SBI PO previous papers available?', 'SBI does not publish its papers. Learn with Anil has its own full-length SBI PO Prelims mock tests in the real pattern, in English and Hindi, with explanations.'),
    ])
ASOF_PAGE['sbi-po-2026-notification.html'] = '16 November 2026'

NEW['ibps-so-2026-notification.html'] = dict(
    exam='ibps-so', board='IBPS', site='ibps.in', crumb='IBPS SO 2026 (CRP SPL-XVI)', faq_asof='16 November 2026',
    title='IBPS SO 2026 (CRP SPL-XVI): Vacancies Revised to 1,043, Mains Held 1 November, Interview Next, Post-wise Posts & Mock Tests | Learn with Anil',
    desc='IBPS Specialist Officer 2026, CRP SPL-XVI: vacancies revised from 745 to 1,043 (IT 376, AFO 370, Law 125, Rajbhasha 102, HR 60, Marketing 10). Prelims '
         '29 August, result 15 October, Mains 1 November 2026; interviews next. The Prelims pattern and free-pattern mock tests.',
    h1='IBPS SO 2026: 1,043 posts, Mains over, interviews next',
    lede='IBPS is recruiting Specialist Officers (Scale I) for the public sector banks through CRP SPL-XVI, for the vacancy year 2027-28. The notification of 30 June '
         '2026 gave 745 posts; IBPS has since raised them to 1,043. The Prelims (29 August) and Mains (1 November 2026) are over; the Mains result and the interviews '
         'come next. Below: the dates, the post-wise vacancies, the selection process and the Prelims pattern.',
    hi='आईबीपीएस एसओ 2026 (CRP SPL-XVI): रिक्तियाँ बढ़कर 1,043। मेन्स परीक्षा 1 नवंबर 2026 को हुई; अब मेन्स का परिणाम और इंटरव्यू।',
    pdf='https://www.ibps.in', pdfname='IBPS CRP SPL-XVI notification (30 June 2026) and the revised vacancy list (27 August 2026), ibps.in',
    related=['sbi-po-2026-notification.html'],
    sections=[
      ('Key dates', 'table', [
        ('Notification', '30 June 2026, CRP SPL-XVI (vacancy year 2027-28)'), ('Online applications', 'July 2026 (closed)'),
        ('Vacancies revised', '745 → 1,035 (20 July) → 1,043 (27 August 2026)'),
        ('Prelims', '29 August 2026 (result 15 October)'), ('Mains', '1 November 2026'),
        ('Interview', 'After the Mains result; IBPS\'s tentative schedule says December 2026 – January 2027'),
        ('Provisional allotment', 'Early 2027 (tentative)'),
      ]),
      ('Post-wise vacancies (revised, 27 August 2026)', 'table+', (['Post (Scale I)', 'Posts'], [
        ('IT Officer', '376'), ('Agricultural Field Officer', '370'), ('Law Officer', '125'), ('Rajbhasha Adhikari', '102'), ('HR / Personnel Officer', '60'),
        ('Marketing Officer', '10'), ('Total', '1,043')])),
      ('', 'note', 'The list is indicative: IBPS may change it again with the banks\' reports. Final selection: Mains and interview, with 80% and 20% weightage.'),
      ('Prelims pattern (IT, AFO, HR, Marketing)', 'table+', (['Section', 'Questions · marks', 'Time'], [
        ('English Language', '25 · 25', '20 minutes'), ('Reasoning', '25 · 25', '20 minutes'), ('Quantitative Aptitude', '25 · 25', '20 minutes'),
        ('Professional Knowledge', '25 · 50', '20 minutes'), ('Total', '100 · 125', '80 minutes')])),
      ('', 'note', 'A quarter of the marks for a question is cut for each wrong answer. Law Officer and Rajbhasha Adhikari candidates have General Awareness '
                   '(banking) in place of Quantitative Aptitude.'),
    ],
    faqs=[
      ('How many vacancies are there in IBPS SO 2026?', '1,043 after the revision of 27 August 2026: IT Officer 376, AFO 370, Law 125, Rajbhasha 102, HR 60 and Marketing 10. The notification first gave 745.'),
      ('When was the IBPS SO Mains 2026?', 'On 1 November 2026. The Prelims was on 29 August and its result came on 15 October 2026.'),
      ('When is the IBPS SO 2026 interview?', 'After the Mains result. IBPS\'s tentative schedule puts the interviews in December 2026 – January 2027.'),
      ('How is the IBPS SO final selection made?', 'On the Mains and interview marks, with 80% and 20% weightage. The Prelims only shortlists for the Mains.'),
      ('Are IBPS SO previous papers available?', 'IBPS does not publish its papers. Learn with Anil has its own IBPS SO Prelims mock tests (IT, AFO, HR and Marketing) in the real pattern, in English and Hindi.'),
    ])
ASOF_PAGE['ibps-so-2026-notification.html'] = '16 November 2026'

NEW['ssc-chsl-2026-notification.html'] = dict(
    exam='ssc-chsl', board='SSC', site='ssc.gov.in', crumb='SSC CHSL 2026', faq_asof='16 November 2026',
    title='SSC CHSL 2026: Tier-1 Exam 30 November – 31 December, 2,536 Vacancies, Pattern with 15-Minute Sectional Timer & Previous Papers | Learn with Anil',
    desc='SSC CHSL 2026 (10+2): 2,536 tentative vacancies for LDC/JSA, DEO and DEO Grade A; Tier-I computer-based exam from 30 November to 31 December 2026. '
         'Dates, age limit 18–27, fee, Tier-I pattern with the new 15-minute sectional timer, Tier-II, pay and free CHSL 2025 Tier-I previous papers.',
    h1='SSC CHSL 2026: Tier-1 from 30 November',
    lede='The Staff Selection Commission\'s Combined Higher Secondary Level (10+2) Examination 2026 fills Lower Divisional Clerk / Junior Secretariat Assistant and '
         'Data Entry Operator posts in central ministries and offices. Applications closed on 7 October; the Tier-I computer-based exam runs from 30 November to '
         '31 December 2026. Below: the dates, posts, eligibility and the exam pattern, with this year\'s change: a 15-minute timer for each Tier-I section.',
    hi='एसएससी सीएचएसएल 2026: 2,536 पद (एलडीसी/जेएसए, डीईओ)। टियर-I कंप्यूटर आधारित परीक्षा 30 नवंबर से 31 दिसंबर 2026 तक। हर सेक्शन के लिए 15 मिनट का अलग टाइमर।',
    pdf='https://ssc.gov.in', pdfname='SSC CHSL 2026 notice (7 September 2026) and the Tier-I schedule, ssc.gov.in',
    related=['ssc-mts-2026-notification.html', 'ssc-cgl-2026-notification.html'],
    sections=[
      ('Key dates', 'table', [
        ('Notification', '7 September 2026'), ('Online applications', '7 September – 7 October 2026 (11 PM); fee till 8 October'),
        ('Correction window', '14 – 16 October 2026'), ('Tier-I (computer-based)', '30 November – 31 December 2026'),
        ('Tier-II', 'Date to be announced by SSC'),
      ]),
      ('Posts and pay', 'table+', (['Post', 'Pay level'], [
        ('Lower Divisional Clerk (LDC) / Junior Secretariat Assistant (JSA)', 'Level 2 (₹19,900 – 63,200)'),
        ('Data Entry Operator (DEO)', 'Level 4 (₹25,500 – 81,100) and Level 5 (₹29,200 – 92,300)'),
        ('Data Entry Operator Grade \'A\'', 'Level 4 (₹25,500 – 81,100)'),
        ('Total vacancies (tentative)', '2,536')])),
      ('Eligibility', 'table', [
        ('Age', '18 – 27 years as on 1 August 2026 (relaxation for SC/ST, OBC, PwBD, ex-servicemen as per rules)'),
        ('Education', 'Class 12 (10+2) or equivalent; DEO Grade \'A\' needs Class 12 Science with Mathematics'),
        ('Fee', '₹100; no fee for women, SC, ST, PwBD and ex-servicemen'),
      ]),
      ('Tier-I pattern', 'table+', (['Section', 'Questions · marks', 'Time'], [
        ('English Language (Basic Knowledge)', '25 · 50', '15 minutes'), ('General Intelligence', '25 · 50', '15 minutes'),
        ('Quantitative Aptitude (Basic Arithmetic Skill)', '25 · 50', '15 minutes'), ('General Awareness', '25 · 50', '15 minutes'),
        ('Total', '100 · 200', '60 minutes')])),
      ('', 'note', 'Half a mark (0.5) is cut for each wrong answer. New in 2026: each section has its own 15-minute timer, so time cannot be moved between sections. '
                   'Tier-I is a screening test; Tier-II (Session I: Mathematics, Reasoning, English, General Awareness and Computer Knowledge, 1 mark cut per wrong '
                   'answer; Session II: skill/typing test) decides the merit list.'),
    ],
    faqs=[
      ('When is the SSC CHSL 2026 Tier-1 exam?', 'From 30 November to 31 December 2026, in many shifts. Your own date, shift and centre are on your SSC admit card.'),
      ('How many vacancies are there in SSC CHSL 2026?', '2,536 tentative vacancies for LDC/JSA, DEO and DEO Grade A. SSC may revise the number before the final result.'),
      ('Is there a sectional time limit in SSC CHSL 2026 Tier-1?', 'Yes. From this cycle each of the four sections has its own 15-minute timer (60 minutes in all).'),
      ('What is the age limit for SSC CHSL 2026?', '18 to 27 years as on 1 August 2026, with the usual relaxation for reserved categories.'),
      ('Where can I practise SSC CHSL previous papers?', 'Learn with Anil has SSC CHSL 2025 Tier-I shift papers with SSC\'s answer key and explanations, in English and Hindi, as timed 60-minute mocks and 15-minute sectionals.'),
    ])
ASOF_PAGE['ssc-chsl-2026-notification.html'] = '16 November 2026'

NEW['ibps-rrb-clerk-2026-notification.html'] = dict(
    exam='ibps-rrb', board='IBPS', site='ibps.in', crumb='IBPS RRB Clerk 2026 (CRP RRBs-XV)', faq_asof='16 November 2026',
    title='IBPS RRB Clerk 2026 (CRP RRBs-XV): Prelims 6, 12 & 13 December, Mains 30 January, Office Assistant Pattern, Eligibility & Mock Tests | Learn with Anil',
    desc='IBPS RRB Office Assistant (Clerk) 2026, CRP RRBs-XV: Prelims on 6, 12 and 13 December 2026, Mains on 30 January 2027. Prelims pattern (Reasoning 40 in 25 '
         'minutes, Numerical Ability 40 in 20 minutes), Mains pattern, age 18–28, eligibility, local language rule and free-pattern mock tests.',
    h1='IBPS RRB Clerk 2026: Prelims on 6, 12 and 13 December',
    lede='IBPS is recruiting Office Assistants (Multipurpose) and Officers for the Regional Rural Banks through CRP RRBs-XV. Applications closed on 21 September 2026. '
         'The Office Assistant (Clerk) Prelims is on 6, 12 and 13 December 2026 and the Mains on 30 January 2027; there is no interview for Office Assistants. '
         'Below: the dates, eligibility and the exam pattern.',
    hi='आईबीपीएस आरआरबी ऑफिस असिस्टेंट (क्लर्क) 2026: प्रारंभिक परीक्षा 6, 12 और 13 दिसंबर 2026, मुख्य परीक्षा 30 जनवरी 2027। प्रारंभिक: तर्कशक्ति 40 (25 मिनट) और संख्यात्मक योग्यता 40 (20 मिनट)।',
    pdf='https://www.ibps.in', pdfname='IBPS CRP RRBs-XV notification (1 September 2026) and IBPS\'s exam schedule, ibps.in',
    related=['ibps-so-2026-notification.html', 'sbi-po-2026-notification.html'],
    sections=[
      ('Key dates (Office Assistant)', 'table', [
        ('Notification', '31 August 2026 (short notice); detailed notification 1 September 2026'), ('Online applications', '1 – 21 September 2026 (closed)'),
        ('Prelims', '6, 12 and 13 December 2026'), ('Mains', '30 January 2027'), ('Provisional allotment', 'After the Mains result (IBPS\'s tentative schedule: February–March 2027)'),
      ]),
      ('Eligibility', 'table', [
        ('Age', '18 – 28 years as on 1 September 2026 (born not earlier than 2 September 1998 and not later than 1 September 2008); relaxation as per rules'),
        ('Education', 'A bachelor\'s degree in any discipline; working knowledge of computers is desirable'),
        ('Local language', 'Proficiency in the official language of the state where the RRB is (studied up to Class 8 or a certificate); otherwise it must be learnt within six months of joining'),
        ('Fee', '₹850; ₹175 for SC, ST, PwBD and ex-servicemen'),
      ]),
      ('Prelims pattern', 'table+', (['Test', 'Questions · marks', 'Time'], [
        ('Reasoning', '40 · 40', '25 minutes'), ('Numerical Ability', '40 · 40', '20 minutes'), ('Total', '80 · 80', '45 minutes')])),
      ('', 'note', 'A quarter of a mark (0.25) is cut for each wrong answer, and candidates must clear the cut-off in each test. The exam is offered in English, Hindi and '
                   'the regional language of the state (for example Telugu in Andhra Pradesh and Telangana).'),
      ('Mains pattern', 'table+', (['Test', 'Questions · marks', 'Time'], [
        ('Reasoning', '40 · 50', '30 minutes'), ('Computer Knowledge', '40 · 20', '15 minutes'), ('General Awareness', '40 · 40', '15 minutes'),
        ('English or Hindi Language', '40 · 40', '30 minutes'), ('Numerical Ability', '40 · 50', '30 minutes'), ('Total', '200 · 200', '120 minutes')])),
      ('', 'note', 'Allotment is on the Mains marks only; the Prelims just shortlists. Vacancies are listed bank-wise and state-wise in the notification and are indicative.'),
    ],
    faqs=[
      ('When is the IBPS RRB Clerk Prelims 2026?', 'On 6, 12 and 13 December 2026 (CRP RRBs-XV, Office Assistant). The Mains is on 30 January 2027.'),
      ('What is the IBPS RRB Clerk Prelims pattern?', 'Reasoning 40 questions in 25 minutes and Numerical Ability 40 questions in 20 minutes: 80 questions, 80 marks, 45 minutes, 0.25 mark cut per wrong answer.'),
      ('Is there an interview for IBPS RRB Office Assistant?', 'No. Office Assistants are allotted on the Mains marks alone. Officer Scale I candidates have an interview.'),
      ('What is the age limit for IBPS RRB Clerk 2026?', '18 to 28 years as on 1 September 2026, with the usual relaxation for reserved categories.'),
      ('Are IBPS RRB previous papers available?', 'IBPS does not publish its papers. Learn with Anil has its own IBPS RRB Clerk Prelims mock tests in the real pattern, in English and Hindi, with 25-minute and 20-minute sectional tests.'),
    ])
ASOF_PAGE['ibps-rrb-clerk-2026-notification.html'] = '16 November 2026'


def apply(NOTIFS):
    for rel, f in FAQS.items():
        if rel in NOTIFS: NOTIFS[rel]['faqs'] = f; NOTIFS[rel]['faq_asof'] = ASOF_PAGE.get(rel, ASOF)
    for rel, N in NEW.items():
        N.setdefault('faq_asof', ASOF_PAGE.get(rel, ASOF))
        NOTIFS[rel] = N
