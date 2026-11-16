// Display names and icons shared by the pages.

export const AREA_NAMES = {
  courts: "Courts & protective orders", health: "Health", services: "Victim services & funding",
  benefits: "Public benefits", housing: "Housing", child_welfare: "Child welfare", immigration: "Immigration",
  education: "Education", firearms: "Firearms", employment: "Employment", financial: "Financial abuse & credit",
  custody: "Custody & family law", privacy: "Privacy & address confidentiality", language: "Language access",
};

export const IDS = [
  { id: "immigrant_vawa", name: "Immigrant", long: "Immigrant & VAWA survivors",
    def: "Immigration status, VAWA, U and T visas, asylum, refugees, noncitizens, public charge, passports." },
  { id: "women_gender", name: "Woman", long: "Women & gender",
    def: "Women, gender, gender-based violence, pregnancy, reproductive health, forced or coerced marriage, dowry." },
  { id: "faith", name: "Faith", long: "Faith & religion",
    def: "Religion, places of worship, clergy, faith leaders, faith-based groups, religious or spiritual needs.",
    note: "No bill in the index is about faith. The bills here mention religion only in a list of protected traits." },
  { id: "language_access", name: "Language", long: "Language access",
    def: "Interpreters, translation, limited English proficiency, culturally specific services.",
    note: "No bill names Punjabi, Hindi, Urdu, Bengali, Gujarati, Tamil, Telugu, Nepali, Arabic, Farsi, Dari or Pashto." },
  { id: "disability", name: "Disability", long: "People with disabilities", def: "Disability, Deaf survivors, sign language." },
  { id: "lgbtq", name: "LGBTQ+", long: "LGBTQ+ survivors", def: "LGBTQ, gender identity." },
  { id: "youth", name: "Youth", long: "Youth", def: "Minors and young people." },
  { id: "elder_dependent_adult", name: "Elder", long: "Elders & dependent adults", def: "Elders and dependent adults." },
  { id: "tribal", name: "Tribal", long: "Tribal communities", def: "Tribes, tribal nations, Native Americans." },
  { id: "rural", name: "Rural", long: "Rural survivors", def: "Rural areas." },
  { id: "military", name: "Military", long: "Military & veterans", def: "Service members, veterans, armed forces, military protective orders." },
];

export const ID_NAME = Object.fromEntries(IDS.map((i) => [i.id, i.long]));

// 24x24 line icons, stroked with currentColor.
export const ICONS = {
  immigrant_vawa: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.7 5.7 3.7 9s-1.2 6.3-3.7 9c-2.5-2.7-3.7-5.7-3.7-9S9.5 5.7 12 3z"/>',
  women_gender: '<circle cx="12" cy="9" r="5.5"/><path d="M12 14.5V22M8.5 18.5h7"/>',
  faith: '<path d="M12 3c1.8 2.2 2.6 3.7 2.6 5a2.6 2.6 0 0 1-5.2 0c0-1.3.8-2.8 2.6-5z"/><path d="M12 10.6V12M8.5 12h7v9h-7z"/>',
  language_access: '<path d="M4 5h10v7H8l-4 3z"/><path d="M14 9h6v7l-3-2h-5v-2"/>',
  disability: '<circle cx="11" cy="4.5" r="1.6"/><path d="M11 7.5v6h5l2 5M7.5 11a5.5 5.5 0 1 0 7.8 6.8"/>',
  lgbtq: '<path d="M3 18a9 9 0 0 1 18 0M6 18a6 6 0 0 1 12 0M9 18a3 3 0 0 1 6 0"/>',
  youth: '<circle cx="12" cy="7" r="2.6"/><path d="M8 21v-6l-2-3 3-2h6l3 2-2 3v6"/>',
  elder_dependent_adult: '<circle cx="10" cy="4.8" r="2.2"/><path d="M10 7.5c-2 1-2.5 3-2.5 5v8.5M10 7.5c1.5 1 2.2 2.5 2.3 4.5l2.2 1.5M16.5 11v10"/>',
  tribal: '<circle cx="12" cy="5" r="2"/><circle cx="5.5" cy="15" r="2"/><circle cx="18.5" cy="15" r="2"/><path d="M8 7.5 6.5 12.5M16 7.5l1.5 5M8 16.5h8"/>',
  rural: '<path d="M12 21v-5M6.5 16h11L12 4z"/><path d="M3 21h18"/>',
  military: '<path d="M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6z"/><path d="m12 8 1.2 2.5 2.8.4-2 2 .5 2.8L12 14.4l-2.5 1.3.5-2.8-2-2 2.8-.4z"/>',
};

export const fmtDate = (d) =>
  d ? new Date(d.length > 10 ? d : d + "T12:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "America/Los_Angeles" }) : "";
