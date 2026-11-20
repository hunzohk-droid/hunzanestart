"""Rebuild the product shelves in index.html from one product list.
Add a new product: put its 720x540 webp in img/, add one line to PRODUCTS, put its ID in a shelf (and in NEW), run:
    python3 tools/build_shelves.py
Every link uses the Etsy Share & Save format https://hunzanestart.etsy.com/listing/<ID>."""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / 'index.html'

# id: (title, image, alt, description, chip)
PRODUCTS = {
    '4602131247': ('Budget by Paycheck', 'img/budget-by-paycheck.webp', 'Budget by Paycheck Google Sheets dashboard', 'Plan each weekly, biweekly or monthly paycheck, with bills, savings and debt in one planner.', 'Google Sheets'),
    '4605515263': ('Biweekly Budget', 'img/biweekly-budget.webp', 'One Sheet Biweekly Budget spreadsheet', 'One sheet for every payday: income, bills, savings and debt on a single page.', 'Google Sheets'),
    '4606098060': ('Monthly & Annual Budget', 'img/monthly-annual-budget.webp', 'Monthly and Annual Budget dashboard', 'Plan each month and see the whole year on a dashboard with charts.', 'Google Sheets'),
    '4603169758': ('Bill Tracker', 'img/bill-tracker.webp', 'Bill Tracker with bill calendar and payment status', 'A bill calendar with paid and not-paid status and monthly totals.', 'Google Sheets'),
    '4606796367': ('Debt Tracker', 'img/debt-tracker.webp', 'Debt Tracker with snowball and avalanche plans', 'List your debts once and compare a snowball plan with an avalanche plan on a dashboard.', 'Google Sheets'),
    '4599275554': ('Small Business Bundle', 'https://i.etsystatic.com/68333470/r/il/da0ee8/8790976797/il_794xN.8790976797_an9e.jpg', 'Small Business Spreadsheet Bundle', 'Bookkeeping, inventory, order tracking, invoices and a pricing calculator in one workbook.', 'Google Sheets'),
    '4609536793': ('Small Business Accounting', 'https://i.etsystatic.com/68333470/r/il/102698/8864822515/il_794xN.8864822515_jnkc.jpg', 'Small Business Accounting bookkeeping spreadsheet', 'Easy bookkeeping: log income and expenses and see your business totals at a glance.', 'Spreadsheet'),
    '4617649899': ('Business Binder', 'img/business-binder.webp', 'Business Binder Google Sheets dashboard on a laptop', 'Orders, stock, clients, suppliers and tasks with a live dashboard, plus 20 printable pages.', 'Google Sheets'),

    '4620009381': ('All-in-One Planner', 'img/all-in-one-planner.webp', 'All-in-One Planner Google Sheets dashboard', 'Plan your days, weeks, goals and habits in one Google Sheet with a live dashboard.', 'Google Sheets'),
    '4620787319': ('Project Management Planner', 'img/project-management.webp', 'Project Management Planner with Gantt chart', 'Projects, tasks and deadlines with a self-updating Gantt chart and dashboard.', 'Sheets + Excel'),
    '4610977522': ('Notion Dashboard', 'img/notion-dashboard.webp', 'Notion Dashboard life planner home page', 'Tasks, projects, goals, habits, money and notes on one calm Notion home page.', 'Notion'),
    '4606848052': ('Perpetual Calendar', 'img/perpetual-calendar.webp', 'Perpetual Calendar for Google Sheets', 'Pick any month and year and the calendar fills itself in, with birthdays and anniversaries.', 'Google Sheets'),
    '4609462330': ('Executive Resume', 'img/executive-resume.webp', 'Executive Resume template with cover letter', 'One and two page executive resume with a matching cover letter and references page.', 'Word · Docs · Canva'),
    '4609589612': ('Professional ATS Resume', 'img/ats-resume.webp', 'Professional ATS-friendly resume template', 'A clean, ATS-friendly resume in one and two page versions, cover letter included.', 'Word · Google Docs'),

    '4608030764': ('Life Binder', 'img/life-binder.webp', 'Life Binder home management binder', 'A home management and emergency binder for the whole family, in Google Sheets with printable pages.', 'Google Sheets'),
    '4598299148': ('Cleaning Planner', 'https://i.etsystatic.com/68333470/r/il/59f30d/8788150322/il_794xN.8788150322_1ogc.jpg', 'Cleaning Planner and checklists', 'Editable cleaning checklists and a planner, plus ready-to-print PDFs.', 'Canva + PDF'),
    '4611048712': ('Weekly Meal Planner', 'img/weekly-meal-planner.webp', 'Weekly Meal Planner with grocery list', 'Plan the week, get the grocery list, and start with 30 recipes already in the sheet.', 'Google Sheets'),
    '4616172372': ('Family Recipes Binder', 'img/family-recipes.webp', 'Family Recipes Binder printable and recipe book', "Keep the family's recipes and stories together: printable binder plus a recipe book in Google Sheets.", 'Sheets + PDF'),
    '4606158298': ('Calorie Tracker', 'img/calorie-tracker.webp', 'Calorie Tracker for Google Sheets', 'A food diary and daily calorie log with a simple dashboard.', 'Google Sheets'),
    '4615351269': ('Health Records Organizer', 'img/health-records.webp', 'Health Records Organizer medical binder', "Your family's medical records in one place: dashboard, 41 printable pages, up to 8 people.", 'Sheets + PDF'),

    '4614573494': ('Wedding Day Binder', 'img/wedding-day-binder.webp', 'Wedding Day Binder planner', 'Countdown dashboard, timeline, vendors and budget for the big day, in 34 pages.', 'Sheets + PDF + Canva'),
    '4610485506': ('Wedding Itinerary Kit', 'img/wedding-itinerary.webp', 'Wedding Itinerary Kit master day timeline', 'Every person, every hour: a master timeline plus bride, groom, bridal party and guest pages.', 'Canva + PDF'),
    '4606864346': ('Hen Night Games', 'img/hen-night-games.webp', 'Hen Night Games printable bundle', '20 clean and silly printable hen party games, in A4 and US Letter.', 'Printable PDF'),
    '4607388149': ('Address Labels', 'img/address-labels.webp', 'Return address labels editable in Canva', '15 return address label designs to edit in Canva, sized for Avery 5160 sheets.', 'Canva'),
    '4611824069': ('Pregnancy Journal', 'img/pregnancy-journal.webp', 'Pregnancy Journal weekly check-in page', 'A week-by-week keepsake with check-ins from week 4 to 40 and bump photo pages.', 'Canva + PDF'),
    '4613815648': ('Birth Plan Template', 'img/birth-plan.webp', 'Birth Plan Template fillable pages', 'Fillable birth preferences with a one-page summary for your nurse, in Letter and A4.', 'Fillable PDF'),

    '4604648249': ('Preschool Curriculum', 'img/preschool-curriculum.webp', 'Preschool Curriculum weekly lesson plans', 'Weekly lesson plans, a skills tracker and progress charts for pre-K at home.', 'Google Sheets'),
    '4605405695': ('Preschool Curriculum Bundle', 'img/preschool-bundle.webp', 'Preschool Curriculum Bundle', 'The curriculum together with name tracing and the learning binder.', 'Google Sheets'),
    '4604670037': ('Name Tracing Maker', 'img/name-tracing.webp', 'Name Tracing Worksheet Maker', 'Type a name of up to 12 letters and print handwriting practice pages.', 'Google Sheets'),
    '4605413074': ('Learning Binder', 'img/learning-binder.webp', 'Learning Binder printable', None, 'Google Sheets'),
    '4606768050': ('Daily Rhythm Cards', 'img/daily-rhythm-cards.webp', 'Daily Rhythm Cards picture routine', "Type your child's day and print 12 picture routine cards and a daily chart.", 'Google Sheets'),
    '4606807949': ('Morning Routine Bundle', 'img/morning-routine-bundle.webp', 'Morning Routine Bundle', 'Daily Rhythm Cards and the Learning Binder maker together in one bundle.', 'Google Sheets'),
}

NEW = ['4620787319', '4620009381', '4617649899']  # newest first, shown in "New in the shop"

SHELVES = [
    ('money', 'Money &amp; business', 'Plan paychecks, track bills, pay down debt and run a small business. Every sheet comes with a filled example so you can see how it works first.',
     ['4602131247', '4605515263', '4606098060', '4603169758', '4606796367', '4599275554', '4609536793', '4617649899']),
    ('planners', 'Planners &amp; career', 'Plan your days and projects, keep your life in one dashboard, and apply for your next job with a clean resume.',
     ['4620009381', '4620787319', '4610977522', '4606848052', '4609462330', '4609589612']),
    ('home', 'Home, health &amp; family', 'Keep the household organised: meals, recipes, cleaning and family records, printable in A4 or US Letter.',
     ['4608030764', '4598299148', '4611048712', '4616172372', '4606158298', '4615351269']),
    ('celebrations', 'Weddings, babies &amp; celebrations', 'Plan the big day, the hen night and the new arrival, with pages everyone can follow.',
     ['4614573494', '4610485506', '4606864346', '4607388149', '4611824069', '4613815648']),
    ('preschool', 'Preschool &amp; homeschool', "Type your child's name once and print personalised pages, routine cards and weekly lesson plans.",
     ['4604648249', '4605405695', '4604670037', '4605413074', '4606768050', '4606807949']),
]


def card(pid, new=False):
    t, img, alt, desc, chip = PRODUCTS[pid]
    badge = '<span class="chip new">New</span>' if new else ''
    return (f'      <article class="card"><img src="{img}" alt="{html.escape(alt)}" loading="lazy" width="720" height="540">'
            f'<div class="body"><h3>{html.escape(t)}</h3><p>{html.escape(desc)}</p><div class="foot"><span class="chip">{chip}</span>{badge}'
            f'<a class="go" href="https://hunzanestart.etsy.com/listing/{pid}">View on Etsy</a></div></div></article>')


def main():
    page = PAGE.read_text(encoding='utf-8')
    # keep the existing Learning Binder wording (only description not restated above)
    m = re.search(r'listing/4605413074.*?$', page, re.M)
    lb = re.search(r'<h3>Learning Binder</h3><p>(.*?)</p>', page)
    if lb:
        t = PRODUCTS['4605413074']; PRODUCTS['4605413074'] = (t[0], t[1], t[2], html.unescape(lb.group(1)), t[4])
    total = sum(len(s[3]) for s in SHELVES)
    assert total == len(PRODUCTS) == len({p for s in SHELVES for p in s[3]}), 'every product must be on exactly one shelf'
    out = ['<!-- SHELVES:START (generated by tools/build_shelves.py) -->',
           '<section class="shelf" id="new">', '  <div class="wrap">',
           '    <div class="shelf-head"><div><span class="eyebrow">Just added</span><h2>New in the shop</h2></div>'
           f'<p>The latest templates from HunzaNestart. {total} digital downloads and counting.</p></div>',
           '    <div class="grid">'] + [card(p, True) for p in NEW] + ['    </div>', '  </div>', '</section>', '']
    for i, (sid, title, blurb, ids) in enumerate(SHELVES, 1):
        out += [f'<section class="shelf" id="{sid}">', '  <div class="wrap">',
                f'    <div class="shelf-head"><div><span class="eyebrow">Shelf {i}</span><h2>{title}</h2></div><p>{blurb}</p></div>',
                '    <div class="grid">'] + [card(p) for p in ids] + ['    </div>', '  </div>', '</section>', '']
    out.append('<!-- SHELVES:END -->')
    block = '\n'.join(out)
    if '<!-- SHELVES:START' in page:
        page = re.sub(r'<!-- SHELVES:START.*?<!-- SHELVES:END -->', lambda _: block, page, flags=re.S)
    else:
        page = re.sub(r'<section class="shelf" id="money">.*?(?=<section class="how")', lambda _: block + '\n\n', page, flags=re.S)
    PAGE.write_text(page, encoding='utf-8')
    print('shelves written:', total, 'products')


if __name__ == '__main__':
    main()
