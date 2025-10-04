interface ProgressStepperProps {
  currentStep: number
  totalSteps: number
}

export function ProgressStepper({ currentStep, totalSteps }: ProgressStepperProps) {
  return (
    <div className="flex items-center justify-center gap-2 mb-6">
      {Array.from({ length: totalSteps }).map((_, index) => (
        <div
          key={index}
          className={`h-1.5 rounded-full transition-all duration-300 ${
            index < currentStep ? "w-8 bg-primary" : index === currentStep ? "w-12 bg-primary" : "w-8 bg-muted"
          }`}
        />
      ))}
    </div>
  )
}
