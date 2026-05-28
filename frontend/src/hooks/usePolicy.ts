import { useMutation, useQueryClient } from '@tanstack/react-query'
import { policyApi } from '@/lib/api'
import { lenderKeys } from './useLenders'
import type { ParsedLenderPreview } from '@/types'

export function useUploadPolicy() {
  return useMutation({
    mutationFn: (file: File) => policyApi.upload(file),
  })
}

export function useImportPolicy(lenderId: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (preview: ParsedLenderPreview) => policyApi.importPolicy(lenderId, preview),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: lenderKeys.detail(lenderId) })
    },
  })
}
