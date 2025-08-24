"use client"

import { useState, useEffect } from "react"
import { toast } from "sonner"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { ChevronLeft, ChevronRight, User, GraduationCap, Briefcase, MapPin, AlertCircle, Loader2 } from "lucide-react"

// Validation schema
const doctorRegistrationSchema = z.object({
  // Personal Information - Step 1
  doctor_id: z.string()
    .min(1, "El ID del doctor es requerido")
    .min(3, "El ID debe tener al menos 3 caracteres")
    .max(20, "El ID no puede exceder 20 caracteres")
    .regex(/^[A-Z0-9]+$/, "El ID solo puede contener letras mayúsculas y números"),
  
  first_name: z.string()
    .min(1, "El nombre es requerido")
    .min(2, "El nombre debe tener al menos 2 caracteres")
    .max(50, "El nombre no puede exceder 50 caracteres")
    .regex(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, "El nombre solo puede contener letras"),
  
  last_name: z.string()
    .min(1, "El apellido es requerido")
    .min(2, "El apellido debe tener al menos 2 caracteres")
    .max(50, "El apellido no puede exceder 50 caracteres")
    .regex(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/, "El apellido solo puede contener letras"),
  
  date_of_birth: z.string()
    .min(1, "La fecha de nacimiento es requerida")
    .refine((date) => {
      const birthDate = new Date(date)
      const today = new Date()
      const age = today.getFullYear() - birthDate.getFullYear()
      return age >= 18 && age <= 100
    }, "Debe tener entre 18 y 100 años"),
  
  gender: z.enum(["M", "F", "O"], {
    errorMap: () => ({ message: "Debe seleccionar un género válido" })
  }),
  
  email: z.string()
    .min(1, "El correo electrónico es requerido")
    .email("Debe ser un correo electrónico válido")
    .max(100, "El correo no puede exceder 100 caracteres"),
  
  phone_number: z.string()
    .min(1, "El número de teléfono es requerido")
    .min(10, "El número debe tener al menos 10 dígitos")
    .regex(/^[\+]?[0-9\s\(\)\-]+$/, "Formato de teléfono inválido"),

  // Education and Credentials - Step 2
  license_number: z.string()
    .min(1, "El número de licencia es requerido")
    .min(5, "El número de licencia debe tener al menos 5 caracteres")
    .max(50, "El número de licencia no puede exceder 50 caracteres"),
  
  medical_school: z.string()
    .min(1, "La escuela de medicina es requerida")
    .min(5, "El nombre debe tener al menos 5 caracteres")
    .max(100, "El nombre no puede exceder 100 caracteres"),
  
  graduation_year: z.string()
    .min(1, "El año de graduación es requerido")
    .refine((year) => {
      const yearNum = parseInt(year)
      const currentYear = new Date().getFullYear()
      return yearNum >= 1950 && yearNum <= currentYear
    }, "Debe ser un año válido entre 1950 y el año actual"),
  



})

type DoctorFormData = z.infer<typeof doctorRegistrationSchema>

interface DoctorApiData {
  doctor_id?: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  specialties?: number[]
  license_number: string
  medical_school: string
  graduation_year: number

  phone_number: string
  email: string
  status?: string
}

const steps = [
  {
    id: 0,
    title: "Información Personal",
    description: "Datos personales básicos",
    icon: User,
  },
  {
    id: 1,
    title: "Educación y Credenciales",
    description: "Educación médica y certificaciones",
    icon: GraduationCap,
  },
]

export default function DoctorRegistrationForm() {
  const [currentStep, setCurrentStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isRegistrationSuccessful, setIsRegistrationSuccessful] = useState(false)
  
  const form = useForm<DoctorFormData>({
    resolver: zodResolver(doctorRegistrationSchema),
    defaultValues: {
      doctor_id: "",
      first_name: "",
      last_name: "",
      date_of_birth: "",
      gender: undefined,
      phone_number: "",
      email: "",
      license_number: "",
      medical_school: "",
      graduation_year: "",

    },
    mode: "onChange" // Validate on change for real-time feedback
  })

  const { control, handleSubmit, formState: { errors }, watch, trigger } = form
  const formData = watch() // Watch all form values

  useEffect(() => {
    const handleResizeObserverError = (e: ErrorEvent) => {
      if (e.message === "ResizeObserver loop completed with undelivered notifications.") {
        e.preventDefault()
        e.stopPropagation()
        return false
      }
    }

    window.addEventListener("error", handleResizeObserverError)
    return () => window.removeEventListener("error", handleResizeObserverError)
  }, [])



  // Step validation mapping
  const stepFields: Record<number, (keyof DoctorFormData)[]> = {
    0: ["doctor_id", "first_name", "last_name", "date_of_birth", "gender", "email", "phone_number"],
    1: ["license_number", "medical_school", "graduation_year"]
  }

  const nextStep = async () => {
    if (currentStep < steps.length - 1) {
      // Validate current step fields
      const fieldsToValidate = stepFields[currentStep]
      const isStepValid = await trigger(fieldsToValidate)
      
      if (isStepValid) {
        setCurrentStep(currentStep + 1)
      } else {
        toast.error("Por favor, corrija los errores antes de continuar")
      }
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const transformFormDataToApiFormat = (formData: DoctorFormData): DoctorApiData => {
    const apiData: DoctorApiData = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      date_of_birth: formData.date_of_birth,
      gender: formData.gender,
      license_number: formData.license_number,
      medical_school: formData.medical_school,
      graduation_year: parseInt(formData.graduation_year) || 0,
      phone_number: formData.phone_number,
      email: formData.email,
    }

    // Add doctor_id if provided
    if (formData.doctor_id.trim()) {
      apiData.doctor_id = formData.doctor_id
    }



    // Set default status
    apiData.status = "ACTIVE"

    return apiData
  }

  const submitToApi = async (apiData: DoctorApiData) => {
    // Use the secure Next.js API route instead of calling external API directly
    const fullUrl = '/api/doctors'
    
    console.log('🚀 Submitting to secure API route:', {
      url: fullUrl,
      method: 'POST',
      data: apiData,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      }
    })
    
    try {
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(apiData),
      })

      console.log('📡 API Response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      })

      if (!response.ok) {
        let errorMessage = `Error del servidor (${response.status})`
        
        try {
          const errorData = await response.json()
          errorMessage = errorData.message || errorData.error || errorData.detail || errorMessage
          
          // Handle validation errors
          if (errorData.errors && Array.isArray(errorData.errors)) {
            errorMessage = errorData.errors.map((err: any) => err.message || err).join(', ')
          }
        } catch (parseError) {
          // If JSON parsing fails, use status text or generic message
          errorMessage = response.statusText || errorMessage
        }
        
        throw new Error(errorMessage)
      }

      const responseData = await response.json()
      console.log('✅ API Success Response:', responseData)
      return responseData
    } catch (error) {
      console.error('❌ API Error:', error)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('No se pudo conectar con el servidor. Verifique su conexión a internet y que el backend esté ejecutándose.')
      }
      throw error
    }
  }

  const onSubmit = async (data: DoctorFormData) => {
    setIsSubmitting(true)
    
    try {
      // Transform form data to API format
      const apiData = transformFormDataToApiFormat(data)
      
      // Submit to API
      const result = await submitToApi(apiData)
      
      console.log("Doctor registration successful:", result)
      toast.success("¡Registro enviado exitosamente!", {
        description: `Dr. ${data.first_name} ${data.last_name} ha sido registrado correctamente en el sistema.`
        
      })
      
      // Show success state
      setIsRegistrationSuccessful(true)
      
    } catch (error) {
      console.error("Error submitting doctor registration:", error)
      toast.error("Error al enviar el registro", {
        description: error instanceof Error ? error.message : "Ocurrió un error inesperado. Por favor, intente nuevamente."
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Helper component for field errors
  const FieldError = ({ error }: { error?: string }) => {
    if (!error) return null
    return (
      <div className="flex items-center gap-1 text-red-400 text-sm mt-1">
        <AlertCircle className="w-4 h-4" />
        <span>{error}</span>
      </div>
    )
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="doctor_id">ID del Doctor *</Label>
              <Controller
                name="doctor_id"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="doctor_id"
                      {...field}
                      placeholder="Ingrese el ID del doctor (ej: DOC001)"
                      className={errors.doctor_id ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.doctor_id?.message} />
                  </>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">Nombre *</Label>
                <Controller
                  name="first_name"
                  control={control}
                  render={({ field }) => (
                    <>
                      <Input
                        id="first_name"
                        {...field}
                        placeholder="Ingrese su nombre"
                        className={errors.first_name ? "border-red-500 focus:border-red-500" : ""}
                      />
                      <FieldError error={errors.first_name?.message} />
                    </>
                  )}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Apellido *</Label>
                <Controller
                  name="last_name"
                  control={control}
                  render={({ field }) => (
                    <>
                      <Input
                        id="last_name"
                        {...field}
                        placeholder="Ingrese su apellido"
                        className={errors.last_name ? "border-red-500 focus:border-red-500" : ""}
                      />
                      <FieldError error={errors.last_name?.message} />
                    </>
                  )}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date_of_birth">Fecha de Nacimiento *</Label>
              <Controller
                name="date_of_birth"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="date_of_birth"
                      type="date"
                      {...field}
                      className={errors.date_of_birth ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.date_of_birth?.message} />
                  </>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Género *</Label>
              <Controller
                name="gender"
                control={control}
                render={({ field }) => (
                  <>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger className={errors.gender ? "border-red-500 focus:border-red-500" : ""}>
                        <SelectValue placeholder="Seleccione género" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="M">Masculino</SelectItem>
                        <SelectItem value="F">Femenino</SelectItem>
                        <SelectItem value="O">Otro</SelectItem>
                      </SelectContent>
                    </Select>
                    <FieldError error={errors.gender?.message} />
                  </>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico *</Label>
              <Controller
                name="email"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="email"
                      type="email"
                      {...field}
                      placeholder="doctor@ejemplo.com"
                      className={errors.email ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.email?.message} />
                  </>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone_number">Número de Teléfono *</Label>
              <Controller
                name="phone_number"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="phone_number"
                      {...field}
                      placeholder="+1 (555) 123-4567"
                      className={errors.phone_number ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.phone_number?.message} />
                  </>
                )}
              />
            </div>
          </div>
        )

      case 1:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="license_number">Número de Licencia Médica *</Label>
              <Controller
                name="license_number"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="license_number"
                      {...field}
                      placeholder="Ingrese su número de licencia médica"
                      className={errors.license_number ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.license_number?.message} />
                  </>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="medical_school">Escuela de Medicina *</Label>
              <Controller
                name="medical_school"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="medical_school"
                      {...field}
                      placeholder="Nombre de su escuela de medicina"
                      className={errors.medical_school ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.medical_school?.message} />
                  </>
                )}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="graduation_year">Año de Graduación *</Label>
              <Controller
                name="graduation_year"
                control={control}
                render={({ field }) => (
                  <>
                    <Input
                      id="graduation_year"
                      type="number"
                      min="1950"
                      max={new Date().getFullYear()}
                      {...field}
                      placeholder="2020"
                      className={errors.graduation_year ? "border-red-500 focus:border-red-500" : ""}
                    />
                    <FieldError error={errors.graduation_year?.message} />
                  </>
                )}
              />
            </div>


          </div>
        )



      default:
        return null
    }
  }

  // Success Screen Component
  const renderSuccessScreen = () => {
    return (
      <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="absolute inset-0">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl will-change-transform animate-float"></div>
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-blue-500/15 rounded-full blur-3xl will-change-transform animate-float-delayed"></div>
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl will-change-transform animate-float-slow"></div>

          <div className="absolute top-1/3 left-1/2 w-2 h-2 bg-white/40 rounded-full will-change-transform animate-sparkle"></div>
          <div className="absolute top-2/3 left-1/4 w-1 h-1 bg-purple-300/60 rounded-full will-change-transform animate-sparkle-delayed"></div>
          <div className="absolute top-1/2 right-1/3 w-1.5 h-1.5 bg-blue-300/50 rounded-full will-change-transform animate-sparkle-slow"></div>
          <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-indigo-300/40 rounded-full will-change-transform animate-sparkle"></div>
        </div>

        {/* Floating QR Code */}
        <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
          <div className="text-center">
            {/* Success Message */}
            <div className="mb-8">
              <h1 className="text-4xl font-bold text-white mb-4">¡Empecemos!</h1>
            </div>
            
            {/* QR Code */}
            <div 
              className="inline-block cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl will-change-transform animate-float-gentle"
              onClick={() => window.open('https://wa.me/+573054567983?text=doctor', '_blank')}
            >
              <div className="backdrop-blur-xl bg-white/10 border-white/20 shadow-2xl rounded-2xl p-8">
                <img 
                  src="/qrcode.svg" 
                  alt="QR Code" 
                  className="w-64 h-64 mx-auto"
                />
              </div>
            </div>


          </div>
        </div>
      </div>
    )
  }

  // Show success screen if registration was successful
  if (isRegistrationSuccessful) {
    return renderSuccessScreen()
  }

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl will-change-transform animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-blue-500/15 rounded-full blur-3xl will-change-transform animate-float-delayed"></div>
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl will-change-transform animate-float-slow"></div>

        <div className="absolute top-1/3 left-1/2 w-2 h-2 bg-white/40 rounded-full will-change-transform animate-sparkle"></div>
        <div className="absolute top-2/3 left-1/4 w-1 h-1 bg-purple-300/60 rounded-full will-change-transform animate-sparkle-delayed"></div>
        <div className="absolute top-1/2 right-1/3 w-1.5 h-1.5 bg-blue-300/50 rounded-full will-change-transform animate-sparkle-slow"></div>
        <div className="absolute bottom-1/3 right-1/4 w-1 h-1 bg-indigo-300/40 rounded-full will-change-transform animate-sparkle"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <Card className="w-full max-w-2xl backdrop-blur-xl bg-white/10 border-white/20 shadow-2xl will-change-transform animate-float-gentle">
          <CardHeader className="text-white">
            <div className="flex items-center justify-between mb-4">
              {steps.map((step, index) => {
                const Icon = step.icon
                return (
                  <div key={step.id} className="flex items-center">
                    <div
                      className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300 ${
                        currentStep >= step.id
                          ? "bg-purple-500 text-white border-purple-400 shadow-lg shadow-purple-500/25"
                          : "bg-white/10 text-white/70 border-white/30"
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>
                    {index < steps.length - 1 && (
                      <div
                        className={`w-12 h-0.5 mx-2 transition-all duration-300 ${currentStep > step.id ? "bg-purple-400" : "bg-white/30"}`}
                      />
                    )}
                  </div>
                )
              })}
            </div>

            <CardTitle className="text-2xl font-bold text-white">{steps[currentStep].title}</CardTitle>
            <CardDescription className="text-white/80">{steps[currentStep].description}</CardDescription>
          </CardHeader>

          <CardContent className="text-white">
            {renderStepContent()}

            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 0}
                className="bg-white/10 border-white/30 text-white hover:bg-white/20 hover:border-white/40 transition-all duration-300"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Anterior
              </Button>

              {currentStep < steps.length - 1 ? (
                <Button
                  onClick={nextStep}
                  className="bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/25 transition-all duration-300"
                >
                  Siguiente
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit(onSubmit)}
                  disabled={isSubmitting}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    "Enviar Registro"
                  )}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
