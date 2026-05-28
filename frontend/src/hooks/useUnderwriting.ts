import { useMutation, useQuery } from '@tanstack/react-query'
import { underwritingApi } from '@/lib/api'

export const underwritingKeys = {
  run: (id: string) => ['underwriting', 'runs', id] as const,
}

export function useTriggerUnderwriting() {
  return useMutation({
    mutationFn: (applicationId: string) => underwritingApi.trigger(applicationId),
  })
}

export function useUnderwritingRun(runId: string) {
  return useQuery({
    queryKey: underwritingKeys.run(runId),
    queryFn: () => underwritingApi.getRun(runId),
    enabled: !!runId,
    // Poll every 2 seconds while the run is pending or running
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'pending' || status === 'running' ? 2000 : false
    },
  })
}
