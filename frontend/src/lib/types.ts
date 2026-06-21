export interface User {
  id: string
  email: string
  is_active: boolean
  is_superuser: boolean
  email_verified: boolean
  mfa_enabled: boolean
  created_at: string
}

export interface MatchResult {
  score: number
  matched_skills: string[]
  missing_skills: string[]
  improvement_suggestions: string[]
}

export interface OutreachMessages {
  dm_first_contact: string
  dm_follow_up: string
  connection_note: string
}

export interface ProfileImprovements {
  headline_before: string
  headline_after: string
  about_section: string
}

export interface FullAnalysisResult {
  match_result: MatchResult | null
  outreach_messages: OutreachMessages | null
  profile_improvements: ProfileImprovements | null
  errors: Record<string, string>
}

export interface AnalysisRecord {
  id: string
  user_id?: string
  company?: string | null
  recruiter_name?: string | null
  status: string
  result?: FullAnalysisResult | null
  created_at: string
}

export interface ProgressEvent {
  analysis_id: string
  event: "progress" | "completed" | "partial_completed" | "failed" | "heartbeat"
  step: string
  progress: number | null
  message: string
  data: FullAnalysisResult | Record<string, never>
}
