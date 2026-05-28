import { useState } from 'react'
import StepIndicator from '@/components/wizard/StepIndicator'
import Step1Business from '@/components/wizard/Step1Business'
import Step2Guarantor from '@/components/wizard/Step2Guarantor'
import Step3Credit from '@/components/wizard/Step3Credit'
import Step4LoanRequest from '@/components/wizard/Step4LoanRequest'
import Step5Review from '@/components/wizard/Step5Review'
import {
  useCreateApplication,
  useAddGuarantor,
  useUpsertBusinessCredit,
  useUpsertLoanRequest,
} from '@/hooks/useApplications'
import type { BusinessCreatePayload, GuarantorCreatePayload, BusinessCreditPayload, LoanRequestPayload } from '@/types'

export default function ApplicationWizard() {
  const [step, setStep] = useState(1)
  const [applicationId, setApplicationId] = useState<string | null>(null)

  const createApp = useCreateApplication()
  const addGuarantor = useAddGuarantor(applicationId ?? '')
  const upsertCredit = useUpsertBusinessCredit(applicationId ?? '')
  const upsertLoan = useUpsertLoanRequest(applicationId ?? '')

  const handleStep1 = async (data: BusinessCreatePayload) => {
    const app = await createApp.mutateAsync(data)
    setApplicationId(app.id)
    setStep(2)
  }

  const handleStep2 = async (data: GuarantorCreatePayload) => {
    await addGuarantor.mutateAsync(data)
    setStep(3)
  }

  const handleStep3 = async (data: BusinessCreditPayload) => {
    await upsertCredit.mutateAsync(data)
    setStep(4)
  }

  const handleStep4 = async (data: LoanRequestPayload) => {
    await upsertLoan.mutateAsync(data)
    setStep(5)
  }

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">New Application</h1>
        <p className="mt-1 text-sm text-gray-500">Complete all steps to submit for underwriting.</p>
      </div>

      <StepIndicator current={step} />

      <div className="card p-6">
        {step === 1 && (
          <Step1Business onNext={handleStep1} loading={createApp.isPending} />
        )}
        {step === 2 && applicationId && (
          <Step2Guarantor
            onNext={handleStep2}
            onBack={() => setStep(1)}
            loading={addGuarantor.isPending}
          />
        )}
        {step === 3 && applicationId && (
          <Step3Credit
            onNext={handleStep3}
            onBack={() => setStep(2)}
            loading={upsertCredit.isPending}
          />
        )}
        {step === 4 && applicationId && (
          <Step4LoanRequest
            onNext={handleStep4}
            onBack={() => setStep(3)}
            loading={upsertLoan.isPending}
          />
        )}
        {step === 5 && applicationId && (
          <Step5Review applicationId={applicationId} onBack={() => setStep(4)} />
        )}

        {createApp.isError && step === 1 && (
          <p className="mt-3 text-sm text-red-600">Failed to save. Please check your inputs and try again.</p>
        )}
      </div>
    </div>
  )
}
