import { useQuery } from '@tanstack/react-query'
import { referenceApi } from '@/lib/api'

export function useRuleTypes() {
  return useQuery({
    queryKey: ['reference', 'rule-types'],
    queryFn: referenceApi.ruleTypes,
    staleTime: Infinity,
  })
}

export function useEquipmentTypes() {
  return useQuery({
    queryKey: ['reference', 'equipment-types'],
    queryFn: referenceApi.equipmentTypes,
    staleTime: Infinity,
  })
}

export function useBusinessTypes() {
  return useQuery({
    queryKey: ['reference', 'business-types'],
    queryFn: referenceApi.businessTypes,
    staleTime: Infinity,
  })
}

export function useStates() {
  return useQuery({
    queryKey: ['reference', 'states'],
    queryFn: referenceApi.states,
    staleTime: Infinity,
  })
}
