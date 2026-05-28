import { useState, useRef } from 'react'
import { useUploadPolicy, useImportPolicy } from '@/hooks/usePolicy'
import { DocumentArrowUpIcon } from '@heroicons/react/24/outline'
import type { ParsedLenderPreview } from '@/types'

interface Props {
  lenderId: string
  onClose: () => void
}

export default function PdfUploadModal({ lenderId, onClose }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)
  const upload = useUploadPolicy()
  const importPolicy = useImportPolicy(lenderId)
  const [preview, setPreview] = useState<ParsedLenderPreview | null>(null)

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const result = await upload.mutateAsync(file)
    setPreview(result)
  }

  const handleImport = async () => {
    if (!preview) return
    await importPolicy.mutateAsync(preview)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="card w-full max-w-lg max-h-[90vh] overflow-y-auto p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">Import from PDF</h2>
        <p className="text-sm text-gray-500 mb-4">
          Upload a lender policy PDF. Claude will extract programs and eligibility rules automatically.
          Review before importing.
        </p>

        {!preview && (
          <div
            className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-300 p-10 cursor-pointer hover:border-brand-400 transition-colors"
            onClick={() => fileRef.current?.click()}
          >
            <DocumentArrowUpIcon className="h-10 w-10 text-gray-300 mb-3" />
            <p className="text-sm font-medium text-gray-600">Click to upload PDF</p>
            <p className="text-xs text-gray-400 mt-1">Lender policy or guidelines document</p>
            <input ref={fileRef} type="file" accept=".pdf" className="hidden" onChange={handleFile} />
          </div>
        )}

        {upload.isPending && (
          <div className="text-center py-8">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600 mb-3" />
            <p className="text-sm text-gray-600">Extracting with Claude...</p>
          </div>
        )}

        {upload.isError && (
          <p className="text-sm text-red-600 mt-2">
            Failed to parse PDF. Ensure ANTHROPIC_API_KEY is configured and the file is a valid PDF.
          </p>
        )}

        {preview && (
          <div className="space-y-4">
            <div className="rounded-lg bg-gray-50 p-4 border border-gray-200">
              <p className="font-semibold text-gray-900">{preview.lender_name}</p>
              {preview.notes && <p className="text-sm text-gray-500 mt-1">{preview.notes}</p>}
              {preview.contact_email && <p className="text-xs text-gray-400 mt-1">{preview.contact_email}</p>}
            </div>

            <div className="space-y-3">
              {preview.programs.map((prog, i) => (
                <div key={i} className="rounded-lg border border-gray-200 p-3">
                  <p className="font-medium text-gray-800 text-sm">{prog.name}</p>
                  {prog.description && <p className="text-xs text-gray-500 mt-0.5">{prog.description}</p>}
                  <div className="mt-2 space-y-1">
                    {prog.rules.map((rule, j) => (
                      <div key={j} className="flex items-center gap-2 text-xs text-gray-600">
                        <span className="font-mono text-gray-400">{rule.rule_type}</span>
                        <span>{rule.label}</span>
                        <span className="ml-auto text-gray-400">w:{rule.weight}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-400 mt-2">{prog.rules.length} rules</p>
                </div>
              ))}
            </div>

            <p className="text-xs text-amber-600">
              Review the extracted data above. It will be imported under the current lender.
            </p>

            {importPolicy.isError && (
              <p className="text-sm text-red-600">Import failed. Please try again.</p>
            )}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          {preview && (
            <button className="btn-primary" onClick={handleImport} disabled={importPolicy.isPending}>
              {importPolicy.isPending ? 'Importing...' : `Import ${preview.programs.length} Program${preview.programs.length !== 1 ? 's' : ''}`}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
