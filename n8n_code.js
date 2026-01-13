// 1. Tomar el texto completo de Gemini
const rawText = $input.first().json.content.parts[0].text;
// 2. Parsear el JSON limpio
const data = JSON.parse(rawText);

// Extraer lugar de emisión de factura del domicilio del proveedor
// Formato esperado: "CALLE NUMERO, CP. XXXXX, CIUDAD, ESTADO, PAIS"
// Resultado: "CIUDAD, ESTADO, PAIS"
const extraerLugarEmision = (domicilio) => {
  if (!domicilio) return "";
  const partes = domicilio.split(",").map((s) => s.trim());
  // Buscar la parte que contiene "CP." y tomar todo después de ella
  const indiceCp = partes.findIndex((p) => p.toUpperCase().startsWith("CP"));
  if (indiceCp !== -1 && partes.length > indiceCp + 1) {
    // Tomar desde después del CP hasta el final
    return partes.slice(indiceCp + 1).join(", ");
  }
  // Si no hay CP, tomar las últimas 3 partes (ciudad, estado, país)
  if (partes.length >= 3) {
    return partes.slice(-3).join(", ");
  }
  return domicilio;
};

// PROVEEDORES
const proveedores = data.proveedores?.map((p) => ({
  id_fiscal: p.id_fiscal || "",
  nombre: p.nombre || "",
  domicilio: p.domicilio || "",
})) || [];

// Extraer facturas correctamente (son objetos con propiedad "numero" y "fecha")
// Filtrar las que NO empiezan con "COVE" y mantener correspondencia factura-fecha-proveedor
const facturasValidas = data.proveedores?.flatMap((p) => {
  const lugarEmision = extraerLugarEmision(p.domicilio || "");
  return p.facturas?.filter((f) => f.numero && !f.numero.toUpperCase().startsWith("COVE"))
    .map((f) => ({
      numero: f.numero,
      fecha: f.fecha || "",
      lugar_emision: lugarEmision
    })) || [];
}) || [];

// Arrays para mantener correspondencia 1:1
const facturasNumeroArray = facturasValidas.map((f) => f.numero);
const fechasFacturaArray = facturasValidas.map((f) => f.fecha);

// Strings para compatibilidad (separados por coma)
const facturasNumero = facturasNumeroArray.join(", ");
const fechasFactura = fechasFacturaArray.join(", ");

// MERCANCIAS (PARTIDAS)
const mercancias = data.partidas?.map((p) => ({
  partida: p.numero_secuencia || "",
  descripcion: p.descripcion || "",
  clasificacion_arancelaria: p.fraccion_arancelaria || "",
  cantidad_umc: p.cantidad_umc || "",
  pais_produccion: p.pais_origen || "",
  pais_procedencia: p.pais_vendedor || "",
})) || [];

// Extraer número de patente (4 dígitos centrales del pedimento)
const numPedimento = data.encabezado?.numero_pedimento || "";
const partesPedimento = numPedimento.split(" ");
const patente = partesPedimento[2] || "";

// Calcular totales de incrementables
const fletes = parseFloat(data.valores_globales?.fletes || 0);
const seguros = parseFloat(data.valores_globales?.seguros || 0);
const fletesSeguros = fletes + seguros;

const embalajes = parseFloat(data.valores_globales?.embalajes || 0);
const otrosIncrementables = parseFloat(data.valores_globales?.otros_incrementables || 0);
const cargaDescarga = embalajes + otrosIncrementables;

const totalIncrementables = fletesSeguros + cargaDescarga;

const precioPagado = data.valores_globales?.precio_pagado || "";

// Fechas
const fechaPedimento = data.encabezado?.fechas?.entrada || "";

// Extraer lugares de emisión para cada factura (correspondencia 1:1 con facturas)
const lugaresEmisionArray = data.proveedores?.flatMap((p) => {
  const lugar = extraerLugarEmision(p.domicilio || "");
  // Repetir el lugar para cada factura válida del proveedor
  const facturasProveedor = p.facturas?.filter((f) =>
    f.numero && !f.numero.toUpperCase().startsWith("COVE")
  ) || [];
  return facturasProveedor.map(() => lugar);
}) || [];

// String con todos los lugares (separados por coma)
const lugarEmisionFactura = lugaresEmisionArray.join(", ");

// Lugares únicos (sin duplicados) para cuando se repite el mismo proveedor
const lugaresUnicos = [...new Set(lugaresEmisionArray)].join(", ");

// SALIDA FINAL
return [
  {
    json: {
      metadatos: {},
      importador: {
        importador_nombre: "MICRO HERROS DE OCCIDENTE, S.A. DE C.V.",
        importador_domicilio: "AVENIDA FRESNOS 43 A COLONIA CIUDAD GRANJA 45010 JALISCO, CIUDAD DE MEXICO, MEXICO",
        importador_calle: "AV. FRESNOS, COL. CD. GRANJA, #43 A",
        importador_cp: "45010, ZAPOPAN, JA,MEX",
        importador_rfc: "MHO921021UDO",
        pedimento: numPedimento,
        fecha_pedimento: fechaPedimento,
        num_factura: facturasNumero,
        fecha_factura: fechasFactura,
        // Arrays para volcado a Excel (correspondencia 1:1)
        facturas: facturasValidas,
      },
      proveedores,
      mercancias,
      determinacion_metodo: {
        compraventa: "s",
        vinculadas: "n",
        restricciones: "n",
        contraprestaciones: "n",
        regalias: "n",
      },
      precio_pagado: {
        precio_pagado: precioPagado,
        indirectos: "0",
        total: precioPagado,
      },
      incrementables: {
        comisiones: "0",
        fletes_seguros: fletesSeguros.toString(),
        carga_descarga: cargaDescarga.toString(),
        materiales_aportados: "0",
        tecnologia_aportada: "0",
        regalias: "0",
        reversiones: "0",
        total: totalIncrementables.toString(),
      },
      no_incrementables: {
        gastos_no_relacionados: "0",
        fletes_seguros: "0",
        gastos_de_construccion: "0",
        armado: "0",
        contribuciones: "0",
        dividendos: "0",
        total: "0",
      },
      aduana: {
        precio_pagado: precioPagado,
        ajustes_incrementables: totalIncrementables.toString(),
      },
      pedimento: {
        num_pedimento: numPedimento,
        fecha_pedimento: fechaPedimento,
        num_factura: facturasNumero,
        fecha_factura: fechasFactura,
        // Arrays para volcado a Excel (correspondencia 1:1)
        facturas: facturasValidas,
        lug_emision_factura: lugarEmisionFactura,
        tipo_factura: "x",
        mas: "",
      },
      suscrito: {
        representante: "Jaime Mayagoitia Orozco",
        rfc_legal: "MAOJ640430AR7",
        fecha_pedimento: fechaPedimento,
      },
      num_patente: {
        patente: patente,
      },
    },
  },
];