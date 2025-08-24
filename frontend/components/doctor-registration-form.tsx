"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { ChevronLeft, ChevronRight, User, GraduationCap, Briefcase, MapPin } from "lucide-react"

interface DoctorFormData {
  // Personal Information
  first_name: string
  last_name: string
  date_of_birth: string
  gender: string
  phone_number: string
  email: string
  office_address: string

  // Professional Information
  license_number: string
  medical_school: string
  graduation_year: string
  board_certifications: string
  years_of_experience: string
  department: string

  // System Information
  is_available: boolean
}

const initialFormData: DoctorFormData = {
  first_name: "",
  last_name: "",
  date_of_birth: "",
  gender: "",
  phone_number: "",
  email: "",
  office_address: "",
  license_number: "",
  medical_school: "",
  graduation_year: "",
  board_certifications: "",
  years_of_experience: "",
  department: "",
  is_available: true,
}

const steps = [
  {
    id: 1,
    title: "Información Personal",
    description: "Datos personales básicos",
    icon: User,
  },
  {
    id: 2,
    title: "Educación y Credenciales",
    description: "Educación médica y certificaciones",
    icon: GraduationCap,
  },
  {
    id: 3,
    title: "Detalles Profesionales",
    description: "Experiencia y especialización",
    icon: Briefcase,
  },
  {
    id: 4,
    title: "Contacto y Disponibilidad",
    description: "Información de contacto y disponibilidad",
    icon: MapPin,
  },
]

export default function DoctorRegistrationForm() {
  const [currentStep, setCurrentStep] = useState(1)
  const [formData, setFormData] = useState<DoctorFormData>(initialFormData)

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

  const updateFormData = (field: keyof DoctorFormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const nextStep = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    // Here you would typically send the data to your backend
    console.log("Submitting doctor registration:", formData)
    alert("¡Registro enviado exitosamente!")
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">Nombre *</Label>
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => updateFormData("first_name", e.target.value)}
                  placeholder="Ingrese su nombre"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Apellido *</Label>
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => updateFormData("last_name", e.target.value)}
                  placeholder="Ingrese su apellido"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="date_of_birth">Fecha de Nacimiento *</Label>
              <Input
                id="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => updateFormData("date_of_birth", e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Género *</Label>
              <Select value={formData.gender} onValueChange={(value) => updateFormData("gender", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione género" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="M">Masculino</SelectItem>
                  <SelectItem value="F">Femenino</SelectItem>
                  <SelectItem value="O">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Correo Electrónico *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => updateFormData("email", e.target.value)}
                placeholder="doctor@ejemplo.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone_number">Número de Teléfono *</Label>
              <Input
                id="phone_number"
                value={formData.phone_number}
                onChange={(e) => updateFormData("phone_number", e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="license_number">Número de Licencia Médica *</Label>
              <Input
                id="license_number"
                value={formData.license_number}
                onChange={(e) => updateFormData("license_number", e.target.value)}
                placeholder="Ingrese su número de licencia médica"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="medical_school">Escuela de Medicina *</Label>
              <Input
                id="medical_school"
                value={formData.medical_school}
                onChange={(e) => updateFormData("medical_school", e.target.value)}
                placeholder="Nombre de su escuela de medicina"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="graduation_year">Año de Graduación *</Label>
              <Input
                id="graduation_year"
                type="number"
                min="1950"
                max={new Date().getFullYear()}
                value={formData.graduation_year}
                onChange={(e) => updateFormData("graduation_year", e.target.value)}
                placeholder="2020"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="board_certifications">Certificaciones de Especialidad</Label>
              <Textarea
                id="board_certifications"
                value={formData.board_certifications}
                onChange={(e) => updateFormData("board_certifications", e.target.value)}
                placeholder="Liste sus certificaciones de especialidad (una por línea)"
                rows={4}
              />
            </div>
          </div>
        )

      case 3:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="years_of_experience">Años de Experiencia *</Label>
              <Input
                id="years_of_experience"
                type="number"
                min="0"
                max="50"
                value={formData.years_of_experience}
                onChange={(e) => updateFormData("years_of_experience", e.target.value)}
                placeholder="5"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="department">Departamento/Especialidad *</Label>
              <Select value={formData.department} onValueChange={(value) => updateFormData("department", value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Seleccione su departamento" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Cardiology">Cardiología</SelectItem>
                  <SelectItem value="Dermatology">Dermatología</SelectItem>
                  <SelectItem value="Emergency Medicine">Medicina de Emergencia</SelectItem>
                  <SelectItem value="Family Medicine">Medicina Familiar</SelectItem>
                  <SelectItem value="Internal Medicine">Medicina Interna</SelectItem>
                  <SelectItem value="Neurology">Neurología</SelectItem>
                  <SelectItem value="Oncology">Oncología</SelectItem>
                  <SelectItem value="Orthopedics">Ortopedia</SelectItem>
                  <SelectItem value="Pediatrics">Pediatría</SelectItem>
                  <SelectItem value="Psychiatry">Psiquiatría</SelectItem>
                  <SelectItem value="Radiology">Radiología</SelectItem>
                  <SelectItem value="Surgery">Cirugía</SelectItem>
                  <SelectItem value="Other">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        )

      case 4:
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="office_address">Dirección del Consultorio *</Label>
              <Textarea
                id="office_address"
                value={formData.office_address}
                onChange={(e) => updateFormData("office_address", e.target.value)}
                placeholder="Ingrese la dirección completa de su consultorio"
                rows={3}
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_available"
                checked={formData.is_available}
                onCheckedChange={(checked) => updateFormData("is_available", checked as boolean)}
              />
              <Label
                htmlFor="is_available"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Actualmente estoy disponible para aceptar nuevos pacientes
              </Label>
            </div>

            <div className="bg-muted p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Resumen del Registro</h3>
              <div className="text-sm space-y-1">
                <p>
                  <strong>Nombre:</strong> {formData.first_name} {formData.last_name}
                </p>
                <p>
                  <strong>Correo:</strong> {formData.email}
                </p>
                <p>
                  <strong>Departamento:</strong> {formData.department}
                </p>
                <p>
                  <strong>Experiencia:</strong> {formData.years_of_experience} años
                </p>
                <p>
                  <strong>Disponible:</strong> {formData.is_available ? "Sí" : "No"}
                </p>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
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

            <CardTitle className="text-2xl font-bold text-white">{steps[currentStep - 1].title}</CardTitle>
            <CardDescription className="text-white/80">{steps[currentStep - 1].description}</CardDescription>
          </CardHeader>

          <CardContent className="text-white">
            {renderStepContent()}

            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
                className="bg-white/10 border-white/30 text-white hover:bg-white/20 hover:border-white/40 transition-all duration-300"
              >
                <ChevronLeft className="w-4 h-4 mr-2" />
                Anterior
              </Button>

              {currentStep < steps.length ? (
                <Button
                  onClick={nextStep}
                  className="bg-purple-600 hover:bg-purple-700 text-white shadow-lg shadow-purple-500/25 transition-all duration-300"
                >
                  Siguiente
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/25 transition-all duration-300"
                >
                  Enviar Registro
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
