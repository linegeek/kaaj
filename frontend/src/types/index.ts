// ---- Lender -----------------------------------------------------------------

export interface Lender {
  id: string
  name: string
  contact_email: string | null
  contact_phone: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LenderDetail extends Lender {
  programs: LenderProgram[]
}

export interface LenderProgram {
  id: string
  lender_id: string
  name: string
  description: string | null
  min_amount: number | null
  max_amount: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProgramDetail extends LenderProgram {
  rules: EligibilityRule[]
}

export interface EligibilityRule {
  id: string
  program_id: string
  rule_type: string
  label: string | null
  weight: number
  parameters: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

// ---- Application ------------------------------------------------------------

export interface Business {
  id: string
  application_id: string
  business_name: string
  dba_name: string | null
  owner_name: string
  owner_email: string
  owner_phone: string | null
  state: string
  business_type: string
  years_in_biz: number
  naics_code: string | null
  annual_revenue: number | null
  employee_count: number | null
}

export interface PersonalGuarantor {
  id: string
  application_id: string
  full_name: string
  ssn_last4: string | null
  credit_score: number | null
  ownership_pct: number | null
}

export interface BusinessCredit {
  id: string
  application_id: string
  fico_sbss: number | null
  experian_intelliscore: number | null
  duns_paydex: number | null
  bankruptcies: number
  liens: number
  judgments: number
  years_in_file: number | null
}

export interface LoanRequest {
  id: string
  application_id: string
  requested_amount: number
  requested_term_mo: number
  equipment_type: string
  equipment_description: string | null
  equipment_year: number | null
  equipment_age_yrs: number | null
  equipment_condition: string | null
  state_of_operation: string | null
  down_payment_pct: number | null
}

export interface Application {
  id: string
  status: string
  created_at: string
  updated_at: string
  business: Business | null
  guarantors: PersonalGuarantor[]
  business_credit: BusinessCredit | null
  loan_request: LoanRequest | null
}

// ---- Underwriting -----------------------------------------------------------

export interface CriteriaCheck {
  rule_type: string
  rule_name: string
  weight: number
  passed: boolean
  reason: string | null
  actual_value: string | null
  skipped: boolean
}

export interface ProgramResult {
  lender_id: string
  lender_name: string
  program_id: string
  program_name: string
  fit_score: number
  passed_count: number
  failed_count: number
  skipped_count: number
  criteria: CriteriaCheck[]
}

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface UnderwritingRun {
  id: string
  application_id: string
  status: RunStatus
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  results: ProgramResult[] | null
  created_at: string
}

// ---- Reference --------------------------------------------------------------

export interface RuleTypeMeta {
  rule_type: string
  label: string
  category: string
  param_schema: Record<string, string>
}

export interface USState {
  code: string
  name: string
}

// ---- Policy (PDF parsing) ---------------------------------------------------

export interface ParsedRulePreview {
  rule_type: string
  label: string | null
  weight: number
  parameters: Record<string, unknown>
}

export interface ParsedProgramPreview {
  name: string
  description: string | null
  min_amount: number | null
  max_amount: number | null
  rules: ParsedRulePreview[]
}

export interface ParsedLenderPreview {
  lender_name: string
  notes: string | null
  contact_email: string | null
  contact_phone: string | null
  programs: ParsedProgramPreview[]
}

// ---- Form payloads (sent to API) --------------------------------------------

export interface BusinessCreatePayload {
  business_name: string
  dba_name?: string
  owner_name: string
  owner_email: string
  owner_phone?: string
  state: string
  business_type: string
  years_in_biz: number
  naics_code?: string
  annual_revenue?: number
  employee_count?: number
}

export interface GuarantorCreatePayload {
  full_name: string
  ssn_last4?: string
  credit_score?: number
  ownership_pct?: number
}

export interface BusinessCreditPayload {
  fico_sbss?: number
  experian_intelliscore?: number
  duns_paydex?: number
  bankruptcies: number
  liens: number
  judgments: number
  years_in_file?: number
}

export interface LoanRequestPayload {
  requested_amount: number
  requested_term_mo: number
  equipment_type: string
  equipment_description?: string
  equipment_year?: number
  equipment_condition?: string
  state_of_operation?: string
  down_payment_pct?: number
}

export interface LenderCreatePayload {
  name: string
  contact_email?: string
  contact_phone?: string
  notes?: string
  is_active?: boolean
}

export interface LenderUpdatePayload extends Partial<LenderCreatePayload> {}

export interface ProgramCreatePayload {
  name: string
  description?: string
  min_amount?: number
  max_amount?: number
  is_active?: boolean
}

export interface ProgramUpdatePayload extends Partial<ProgramCreatePayload> {}

export interface RuleCreatePayload {
  rule_type: string
  label?: string
  weight: number
  parameters: Record<string, unknown>
  is_active?: boolean
}

export interface RuleUpdatePayload extends Partial<RuleCreatePayload> {}
