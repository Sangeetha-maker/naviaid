import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

export const resources = {
  en: {
    translation: {
      // Nav
      home: 'Home',
      search: 'Search',
      dashboard: 'Dashboard',
      profile: 'Profile',
      admin: 'Admin',
      logout: 'Logout',
      login: 'Login',

      // Onboarding
      welcome: 'Welcome to NaviAid',
      welcome_sub: 'Find government schemes, scholarships & jobs tailored for you.',
      get_started: 'Get Started',
      next: 'Next',
      back: 'Back',
      finish: 'Finish Setup',
      step: 'Step',
      of: 'of',

      // Profile fields
      name: 'Full Name',
      age: 'Age',
      gender: 'Gender',
      district: 'District',
      caste: 'Caste Category',
      annual_income: 'Annual Family Income (₹)',
      education: 'Highest Education',
      occupation: 'Current Occupation',
      interested_categories: 'Interested In',

      // Categories
      scholarship: 'Scholarship',
      job: 'Job',
      health: 'Health',
      loan: 'Loan',
      housing: 'Housing',
      agriculture: 'Agriculture',
      skill_training: 'Skill Training',

      // Search
      search_placeholder: 'Search schemes, jobs, scholarships...',
      voice_search: 'Voice Search',
      filters: 'Filters',
      clear_filters: 'Clear Filters',
      results: 'Results',
      no_results: 'No results found.',

      // Cards
      eligibility: 'Eligibility',
      apply_now: 'Apply Now',
      learn_more: 'Learn More',
      match_score: 'Match',
      deadline: 'Deadline',
      benefit: 'Benefit',

      // Dashboard
      my_recommendations: 'My Recommendations',
      saved: 'Saved',
      applied: 'Applied',
      loading: 'Loading...',
      error_load: 'Failed to load. Please try again.',
      retry: 'Retry',

      // Voice
      listening: 'Listening...',
      tap_to_speak: 'Tap to Speak',
      voice_not_supported: 'Voice not supported on this device.',

      // Auth
      sign_in: 'Sign In',
      sign_up: 'Sign Up',
      email: 'Email',
      password: 'Password',
      or_continue: 'or continue with',
      google: 'Google',
      dont_have_account: "Don't have an account?",
      already_have_account: 'Already have an account?',
    },
  },
  ta: {
    translation: {
      home: 'முகப்பு',
      search: 'தேடு',
      dashboard: 'டாஷ்போர்டு',
      profile: 'சுயவிவரம்',
      admin: 'நிர்வாகம்',
      logout: 'வெளியேறு',
      login: 'உள்நுழை',
      welcome: 'NaviAid-க்கு வரவேற்கிறோம்',
      welcome_sub: 'உங்களுக்கான அரசு திட்டங்கள், உதவித்தொகை மற்றும் வேலைகளை கண்டறியுங்கள்.',
      get_started: 'தொடங்கு',
      next: 'அடுத்து',
      back: 'பின்',
      finish: 'அமைப்பை முடி',
      step: 'படி',
      of: '/',
      name: 'முழு பெயர்',
      age: 'வயது',
      gender: 'பாலினம்',
      district: 'மாவட்டம்',
      caste: 'சாதி வகை',
      annual_income: 'ஆண்டு குடும்ப வருமானம் (₹)',
      education: 'உயர் கல்வி',
      occupation: 'தொழில்',
      interested_categories: 'விருப்பங்கள்',
      scholarship: 'உதவித்தொகை',
      job: 'வேலை',
      health: 'சுகாதாரம்',
      loan: 'கடன்',
      housing: 'வீடு',
      agriculture: 'விவசாயம்',
      skill_training: 'திறன் பயிற்சி',
      search_placeholder: 'திட்டங்கள், வேலைகள் தேடுங்கள்...',
      voice_search: 'குரல் தேடல்',
      filters: 'வடிகட்டிகள்',
      clear_filters: 'அழி',
      results: 'முடிவுகள்',
      no_results: 'எதுவும் கிடைக்கவில்லை.',
      eligibility: 'தகுதி',
      apply_now: 'விண்ணப்பிக்கவும்',
      learn_more: 'மேலும் அறிக',
      match_score: 'பொருத்தம்',
      deadline: 'கடைசி தேதி',
      benefit: 'பலன்',
      my_recommendations: 'என் பரிந்துரைகள்',
      saved: 'சேமிக்கப்பட்டவை',
      applied: 'விண்ணப்பிக்கப்பட்டவை',
      loading: 'ஏற்றுகிறது...',
      error_load: 'தோல்வி. மீண்டும் முயற்சிக்கவும்.',
      retry: 'மீண்டும் முயற்சி',
      listening: 'கேட்கிறது...',
      tap_to_speak: 'பேச தட்டவும்',
      voice_not_supported: 'இந்த சாதனத்தில் குரல் ஆதரிக்கப்படவில்லை.',
      sign_in: 'உள்நுழை',
      sign_up: 'பதிவு செய்',
      email: 'மின்னஞ்சல்',
      password: 'கடவுச்சொல்',
      or_continue: 'அல்லது தொடரவும்',
      google: 'கூகுள்',
      dont_have_account: 'கணக்கு இல்லையா?',
      already_have_account: 'ஏற்கனவே கணக்கு உள்ளதா?',
    },
  },
}

i18n.use(initReactI18next).init({
  resources,
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
