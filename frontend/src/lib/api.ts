import axios from 'axios'
import type {
  Application, BusinessCreatePayload, BusinessCreditPayload, GuarantorCreatePayload,
  LoanRequestPayload, PersonalGuarantor, BusinessCredit, LoanRequest,
  Lender, LenderDetail, LenderProgram, ProgramDetail, EligibilityRule,
  LenderCreatePayload, LenderUpdatePayload,
  ProgramCreatePayload, ProgramUpdatePayload,
  RuleCreatePayload, RuleUpdatePayload,
  UnderwritingRun, RuleTypeMeta, USState, ParsedLenderPreview,
} from '@/types'

const http = axios.create({ baseURL: '/api/v1' })

// ---- Applications -----------------------------------------------------------

export const applicationsApi = {
  create: (data: BusinessCreatePayload) =>
    http.post<Application>('/applications', data).then(r => r.data),

  get: (id: string) =>
    http.get<Application>(`/applications/${id}`).then(r => r.data),

  addGuarantor: (appId: string, data: GuarantorCreatePayload) =>
    http.post<PersonalGuarantor>(`/applications/${appId}/guarantors`, data).then(r => r.data),

  upsertBusinessCredit: (appId: string, data: BusinessCreditPayload) =>
    http.put<BusinessCredit>(`/applications/${appId}/business-credit`, data).then(r => r.data),

  upsertLoanRequest: (appId: string, data: LoanRequestPayload) =>
    http.put<LoanRequest>(`/applications/${appId}/loan-request`, data).then(r => r.data),
}

// ---- Underwriting -----------------------------------------------------------

export const underwritingApi = {
  trigger: (applicationId: string) =>
    http.post<UnderwritingRun>('/underwriting/run', { application_id: applicationId }).then(r => r.data),

  getRun: (runId: string) =>
    http.get<UnderwritingRun>(`/underwriting/runs/${runId}`).then(r => r.data),
}

// ---- Lenders ----------------------------------------------------------------

export const lendersApi = {
  list: () =>
    http.get<Lender[]>('/lenders').then(r => r.data),

  get: (id: string) =>
    http.get<LenderDetail>(`/lenders/${id}`).then(r => r.data),

  create: (data: LenderCreatePayload) =>
    http.post<Lender>('/lenders', data).then(r => r.data),

  update: (id: string, data: LenderUpdatePayload) =>
    http.put<Lender>(`/lenders/${id}`, data).then(r => r.data),

  delete: (id: string) =>
    http.delete(`/lenders/${id}`),

  // Programs
  listPrograms: (lenderId: string) =>
    http.get<LenderProgram[]>(`/lenders/${lenderId}/programs`).then(r => r.data),

  getProgram: (lenderId: string, programId: string) =>
    http.get<ProgramDetail>(`/lenders/${lenderId}/programs/${programId}`).then(r => r.data),

  createProgram: (lenderId: string, data: ProgramCreatePayload) =>
    http.post<LenderProgram>(`/lenders/${lenderId}/programs`, data).then(r => r.data),

  updateProgram: (lenderId: string, programId: string, data: ProgramUpdatePayload) =>
    http.put<LenderProgram>(`/lenders/${lenderId}/programs/${programId}`, data).then(r => r.data),

  deleteProgram: (lenderId: string, programId: string) =>
    http.delete(`/lenders/${lenderId}/programs/${programId}`),

  // Rules
  listRules: (lenderId: string, programId: string) =>
    http.get<EligibilityRule[]>(`/lenders/${lenderId}/programs/${programId}/rules`).then(r => r.data),

  createRule: (lenderId: string, programId: string, data: RuleCreatePayload) =>
    http.post<EligibilityRule>(`/lenders/${lenderId}/programs/${programId}/rules`, data).then(r => r.data),

  updateRule: (lenderId: string, programId: string, ruleId: string, data: RuleUpdatePayload) =>
    http.put<EligibilityRule>(`/lenders/${lenderId}/programs/${programId}/rules/${ruleId}`, data).then(r => r.data),

  deleteRule: (lenderId: string, programId: string, ruleId: string) =>
    http.delete(`/lenders/${lenderId}/programs/${programId}/rules/${ruleId}`),
}

// ---- Reference --------------------------------------------------------------

export const referenceApi = {
  ruleTypes: () =>
    http.get<RuleTypeMeta[]>('/reference/rule-types').then(r => r.data),

  equipmentTypes: () =>
    http.get<string[]>('/reference/equipment-types').then(r => r.data),

  businessTypes: () =>
    http.get<string[]>('/reference/business-types').then(r => r.data),

  states: () =>
    http.get<USState[]>('/reference/states').then(r => r.data),
}

// ---- Policy parsing ---------------------------------------------------------

export const policyApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return http.post<ParsedLenderPreview>('/parse-policy/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },

  importPolicy: (lenderId: string, preview: ParsedLenderPreview) =>
    http.post('/parse-policy/import', { lender_id: lenderId, preview }).then(r => r.data),
}
