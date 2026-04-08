export interface Student {
  id: string;
  email: string;
  full_name: string;
  department: 'CSE' | 'IT' | 'ECE';
  year: number;
  cgpa: number;
  learning_pace: 'slow' | 'moderate' | 'fast';
  role: 'student' | 'admin' | 'faculty';
  is_active: boolean;
  created_at: string;
}

export interface SkillAssessment {
  subject: string;
  self_rating: number;
  peer_rating: number;
  grade_points: number;
}

export interface AvailabilitySlot {
  day_of_week: number;
  slot: 'morning' | 'afternoon' | 'evening';
  is_available: boolean;
}

export interface GroupMember {
  id: string;
  full_name: string;
  department: string;
  year: number;
  cgpa: number;
  learning_pace: string;
  strengths: string[];
  weaknesses: string[];
}

export interface StudyGroup {
  id: string;
  name: string;
  department: string;
  status: string;
  members: GroupMember[];
  complementary_score: number;
  schedule_overlap_count: number;
  goal_similarity_score: number;
  suggested_meeting_times: string[];
}

export interface HealthScore {
  group_id: string;
  health_score: number;
  factors: Record<string, number>;
  recommendations: string[];
}

export interface Feedback {
  reviewee_id: string;
  rating: number;
  helpfulness_score: number;
  comment: string;
  is_anonymous: boolean;
}

export interface Recommendation {
  title: string;
  url: string;
  type: string;
  subject: string;
  relevance_score: number;
}

export interface AuthState {
  token: string | null;
  refreshToken: string | null;
  student: Student | null;
  isAuthenticated: boolean;
}

export interface SkillExchangeItem {
  subject: string;
  teacher_id: string;
  teacher_name: string;
  learner_id: string;
  learner_name: string;
}

export interface Session {
  id: string;
  group_id: string;
  scheduled_at: string;
  duration_minutes: number;
  topic: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  notes?: string;
}

export interface ReceivedFeedback {
  id: string;
  rating: number;
  helpfulness_score: number;
  comment: string;
  is_anonymous: boolean;
  created_at: string;
}

export interface Mentor {
  id: string;
  full_name: string;
  department: string;
  year: number;
  strong_subjects: string[];
  cgpa: number;
}

export interface AdminDashboard {
  total_students: number;
  total_groups: number;
  avg_health_score: number;
  groups_by_department: Record<string, number>;
  ungrouped_students: number;
}
