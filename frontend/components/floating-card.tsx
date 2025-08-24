"use client"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sparkles, Heart, Star } from "lucide-react"

export default function FloatingCard() {
  return (
    <div className="relative min-h-screen flex items-center justify-center p-4 overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-accent/20 via-primary/10 to-muted animate-gradient"></div>

        {/* Floating shapes */}
        <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-accent/30 rounded-full blur-xl animate-wave"></div>
        <div className="absolute top-3/4 right-1/4 w-24 h-24 bg-primary/20 rounded-full blur-lg animate-pulse-glow"></div>
        <div className="absolute bottom-1/4 left-1/3 w-40 h-40 bg-muted/40 rounded-full blur-2xl animate-float"></div>

        {/* Sparkle effects */}
        <div className="absolute top-1/3 right-1/3 animate-pulse-glow">
          <Sparkles className="w-6 h-6 text-accent/60" />
        </div>
        <div className="absolute bottom-1/3 left-1/5 animate-float">
          <Star className="w-4 h-4 text-primary/50" />
        </div>
        <div className="absolute top-1/5 right-1/5 animate-wave">
          <Heart className="w-5 h-5 text-accent/40" />
        </div>
      </div>

      <Card className="relative z-10 w-full max-w-md animate-float backdrop-blur-sm bg-card/80 border-border/50 shadow-2xl hover:shadow-accent/20 transition-all duration-500 hover:scale-105">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto w-16 h-16 bg-gradient-to-br from-accent to-primary rounded-full flex items-center justify-center mb-4 animate-pulse-glow">
            <Sparkles className="w-8 h-8 text-accent-foreground" />
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Tarjeta Flotante
          </CardTitle>
          <CardDescription className="text-muted-foreground">
            Una experiencia visual elegante con animaciones suaves
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <p className="text-card-foreground leading-relaxed">
            Esta tarjeta flotante presenta un fondo animado con formas que se mueven suavemente, creando una experiencia
            visual moderna y atractiva.
          </p>

          <div className="flex items-center justify-center space-x-2 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
            <span>Diseño moderno</span>
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span>Animaciones suaves</span>
            <div className="w-2 h-2 bg-accent rounded-full animate-pulse"></div>
          </div>
        </CardContent>

        <CardFooter className="flex flex-col space-y-3">
          <Button
            className="w-full bg-gradient-to-r from-accent to-primary hover:from-primary hover:to-accent transition-all duration-300 transform hover:scale-105"
            size="lg"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Explorar Más
          </Button>

          <Button
            variant="outline"
            className="w-full border-accent/50 text-accent hover:bg-accent/10 transition-all duration-300 bg-transparent"
          >
            Más Información
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
