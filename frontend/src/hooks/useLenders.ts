import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { lendersApi } from '@/lib/api'
import type { LenderCreatePayload, LenderUpdatePayload, ProgramCreatePayload, ProgramUpdatePayload, RuleCreatePayload, RuleUpdatePayload } from '@/types'

export const lenderKeys = {
  all: ['lenders'] as const,
  detail: (id: string) => ['lenders', id] as const,
  programs: (id: string) => ['lenders', id, 'programs'] as const,
  program: (lenderId: string, programId: string) => ['lenders', lenderId, 'programs', programId] as const,
}

export function useLenders() {
  return useQuery({ queryKey: lenderKeys.all, queryFn: lendersApi.list })
}

export function useLender(id: string) {
  return useQuery({ queryKey: lenderKeys.detail(id), queryFn: () => lendersApi.get(id) })
}

export function useCreateLender() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: LenderCreatePayload) => lendersApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.all }),
  })
}

export function useUpdateLender(id: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: LenderUpdatePayload) => lendersApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: lenderKeys.all })
      qc.invalidateQueries({ queryKey: lenderKeys.detail(id) })
    },
  })
}

export function useDeleteLender() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => lendersApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.all }),
  })
}

// Programs
export function useProgram(lenderId: string, programId: string) {
  return useQuery({
    queryKey: lenderKeys.program(lenderId, programId),
    queryFn: () => lendersApi.getProgram(lenderId, programId),
  })
}

export function useCreateProgram(lenderId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ProgramCreatePayload) => lendersApi.createProgram(lenderId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.detail(lenderId) }),
  })
}

export function useUpdateProgram(lenderId: string, programId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ProgramUpdatePayload) => lendersApi.updateProgram(lenderId, programId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: lenderKeys.detail(lenderId) })
      qc.invalidateQueries({ queryKey: lenderKeys.program(lenderId, programId) })
    },
  })
}

export function useDeleteProgram(lenderId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (programId: string) => lendersApi.deleteProgram(lenderId, programId),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.detail(lenderId) }),
  })
}

// Rules
export function useCreateRule(lenderId: string, programId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: RuleCreatePayload) => lendersApi.createRule(lenderId, programId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.program(lenderId, programId) }),
  })
}

export function useUpdateRule(lenderId: string, programId: string, ruleId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: RuleUpdatePayload) => lendersApi.updateRule(lenderId, programId, ruleId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.program(lenderId, programId) }),
  })
}

export function useDeleteRule(lenderId: string, programId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (ruleId: string) => lendersApi.deleteRule(lenderId, programId, ruleId),
    onSuccess: () => qc.invalidateQueries({ queryKey: lenderKeys.program(lenderId, programId) }),
  })
}
