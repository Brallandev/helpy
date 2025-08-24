import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    // Get the API token from server-side environment variables (not exposed to browser)
    const authToken = process.env.API_TOKEN
    const apiBaseUrl = process.env.API_BASE_URL || 'http://localhost:8000/api'
    
    if (!authToken) {
      console.error('❌ API_TOKEN not configured in server environment')
      return NextResponse.json(
        { 
          error: 'Token de autenticación no configurado en el servidor',
          message: 'Por favor, configure API_TOKEN en las variables de entorno del servidor.'
        },
        { status: 500 }
      )
    }

    // Parse the request body
    const apiData = await request.json()
    
    const fullUrl = `${apiBaseUrl}/doctors/`
    
    console.log('🚀 Server-side API call:', {
      url: fullUrl,
      method: 'POST',
      hasToken: !!authToken,
      hasData: !!apiData,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer [REDACTED]', // Don't log the actual token
      }
    })
    
    // Make the API call server-side with the secure token
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(apiData),
    })

    console.log('📡 External API Response:', {
      status: response.status,
      statusText: response.statusText,
      headers: Object.fromEntries(response.headers.entries())
    })

    // Get response data
    const responseData = await response.text()
    let parsedData
    
    try {
      parsedData = JSON.parse(responseData)
    } catch (e) {
      parsedData = { message: responseData }
    }

    if (!response.ok) {
      console.error('❌ External API error:', {
        status: response.status,
        statusText: response.statusText,
        data: parsedData
      })
      
      return NextResponse.json(
        {
          error: `Error del servidor externo (${response.status})`,
          message: parsedData.message || parsedData.detail || response.statusText,
          details: parsedData
        },
        { status: response.status }
      )
    }

    console.log('✅ Doctor registration successful')
    
    // Return the successful response
    return NextResponse.json(parsedData, { status: response.status })
    
  } catch (error) {
    console.error('❌ Server error in doctor registration:', error)
    
    return NextResponse.json(
      {
        error: 'Error interno del servidor',
        message: 'Ocurrió un error al procesar la solicitud. Por favor, inténtelo de nuevo.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
