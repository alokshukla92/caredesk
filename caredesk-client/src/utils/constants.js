export const API_BASE = '/server/ragnar_hackathon_alok_swapnil_function';

export const STATUS_COLORS = {
  booked: 'bg-blue-100 text-blue-800',
  'in-queue': 'bg-yellow-100 text-yellow-800',
  'in-consultation': 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

export const STATUS_LABELS = {
  booked: 'Booked',
  'in-queue': 'In Queue',
  'in-consultation': 'With Doctor',
  completed: 'Completed',
  cancelled: 'Cancelled',
};

export const SENTIMENT_COLORS = {
  positive: 'text-green-600',
  negative: 'text-red-600',
  neutral: 'text-gray-500',
};

export const GENDERS = ['Male', 'Female', 'Other'];

export const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];

export const SPECIALTIES = [
  'General Medicine', 'Cardiology', 'Dermatology', 'ENT',
  'Gynecology', 'Neurology', 'Ophthalmology', 'Orthopedics',
  'Pediatrics', 'Psychiatry', 'Pulmonology', 'Urology',
];
