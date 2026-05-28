import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { applicationsApi } from '@/lib/api'
import type {
  BusinessCreatePayload, GuarantorCreatePayload,
  BusinessCreditPayload, LoanRequestPayload,
} from '@/types'

export const applicationKeys = {
  detail: (id: string) => ['applications', id] as const,
}

export function useApplication(id: string) {
  return useQuery({
    queryKey: applicationKeys.detail(id),
    queryFn: () => applicationsApi.get(id),
    enabled: !!id,
  })
}

export function useCreateApplication() {
  return useMutation({
    mutationFn: (data: BusinessCreatePayload) => applicationsApi.create(data),
  })
}

export function useAddGuarantor(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: GuarantorCreatePayload) => applicationsApi.addGuarantor(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: applicationKeys.detail(appId) }),
  })
}

export function useUpsertBusinessCredit(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: BusinessCreditPayload) => applicationsApi.upsertBusinessCredit(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: applicationKeys.detail(appId) }),
  })
}

export function useUpsertLoanRequest(appId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: LoanRequestPayload) => applicationsApi.upsertLoanRequest(appId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: applicationKeys.detail(appId) }),
  })
}
