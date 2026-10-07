import { chromium } from '../../.capture-tools/node_modules/playwright/index.mjs'
import { spawn } from 'node:child_process'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..')
const output = path.join(root, 'docs/screenshots')
const origin = 'http://127.0.0.1:5177'
const user = {
  id: 'demo-user', username: 'ana.demo', firstName: 'Ana', lastName: 'Silva',
  fullName: 'Ana Silva', email: 'ana@example.test', roleDisplay: 'Analista',
  authenticated: true, authorized: true, isActive: true, isStaff: true, status: 'A',
  groups: [{ name: 'Administrador' }], projects: [], pictureUrl: '',
  permissions: ['view_user', 'add_project', 'change_project', 'view_project',
    'can_authorize_users', 'add_creditor', 'change_creditor', 'add_calculation', 'change_calculation'],
}
const recovering = {
  id: 'demo-recovering', entity: { name: 'Empresa Exemplo Ltda.', legalNumber: '00000000000100' },
  creditors: [], total: 2,
}
const project = {
  id: 'demo-project', description: 'Recuperação Judicial — Empresa Exemplo',
  processNumber: '0000000-00.2026.8.00.0000', createdAt: '2026-10-01T10:00:00',
  status: 'a', statusDisplay: 'Em andamento', isAdm: false,
  dateRjRequest: '2026-09-01', dateRjFiling: '2026-09-15', dateCitation: '2026-09-20',
  projectStart: '2026-09-01', projectEnd: '2026-12-31',
  engagement: { numbers: ['DEMO-2026'], createUser: user },
  financialPartner: user, legalManager: user, calculationManager: user,
  projectUsers: [{ ...user, idUser: user.id, groups: [{ name: 'Executor' }] }],
  recoverings: [recovering], judge: { description: 'Juízo demonstrativo' },
  lawyer: { description: 'Representante demonstrativo' },
  court: { description: 'Vara demonstrativa' }, region: { description: 'Comarca exemplo' },
}
const creditors = [
  { id: 'demo-creditor', entity: { name: 'Credor Exemplo A', legalNumber: '00000000000' },
    recoveringId: recovering.id, personType: 'Pessoa física', claimCreditor: [],
    admission: '2022-01-10', dismissal: '2026-08-30' },
  { id: 'demo-creditor-b', entity: { name: 'Fornecedor Exemplo B', legalNumber: '00000000000200' },
    recoveringId: recovering.id, personType: 'Pessoa jurídica', claimCreditor: [] },
]
const calculation = {
  id: 'demo-calculation', number: '001', creditor: creditors[0], step: 'S',
  stepDisplay: 'A calcular', occurrenceDisplay: 'Trabalhista', allFunds: [],
  classes: [], claims: [], credits: [], incident: { id: 'demo-incident', number: 'Incidente demonstrativo' },
  rate: { id: 'demo-rate', description: 'Índice demonstrativo' }, criterion: {},
}
const options = {
  occurrenceOptions: [{ id: 'T', legend: 'Trabalhista' }],
  stepCalculationOptions: [{ id: 'C', legend: 'A revisar' }, { id: 'E', legend: 'A aprovar' }],
  personTypeOptions: [], rolesOptions: [], statusOptions: [],
  classesOptions: [{ id: 'I', legend: 'Classe I — Trabalhista' }],
  classeOptions: [{ id: 'I', legend: 'Classe I — Trabalhista' }],
  coinOptions: [{ id: 'BRL', legend: 'Real (R$)' }],
}
const pagination = (results) => ({ data: { count: results.length, results } })
function response(url) {
  const endpoint = new URL(url).pathname.split('/api/')[1] || ''
  if (endpoint === 'drfmsal_signstatus/') return { profile: user }
  if (endpoint === 'user/detail/') return { user: { ...user, userPermissions: user.permissions.map(codename => ({ codename })) } }
  if (endpoint === 'emails/') return { users: [{ email: 'gestor@example.test' }] }
  if (endpoint === 'users/') return [user, { ...user, id: 'demo-reviewer', firstName: 'Bruno',
    lastName: 'Costa', fullName: 'Bruno Costa', email: 'bruno@example.test', groups: [{ name: 'Revisor' }] }]
  if (endpoint === 'groups/') return { groups: user.groups }
  if (endpoint.includes('project_user')) return { projectUser: [project.id] }
  if (endpoint === 'v1/big_number/dashboard/') return {
    rangeForDays: [{ day: '2026-10-01', total: 2 }, { day: '2026-10-02', total: 3 }, { day: '2026-10-03', total: 1 }],
    rangeForMonth: [], byPhase: { adm: 0, judicial: 1 },
    projectStatus: { countStatus: [{ status: 'a', total: 1 }], countUsers: [{ username: 'Ana Silva', total: 1 }] },
  }
  if (endpoint === `v1/big_number/project/${project.id}/`) return {
    totalCreditor: 2, totalSumCreditors: 15000,
    byStep: [{ step: 'S', stepDisplay: 'A calcular', total: 1 }],
    totalClassesCreditor: [{ classesDisplay: 'Classe I - Trabalhista', quantity: 1, totalHistorical: 12000, totalCalculated: 15000 }],
  }
  if (endpoint.includes('big_number')) return { bigNumberCalc: {} }
  if (endpoint === 'v1/projects/') return pagination([project])
  if (endpoint === `v1/projects/${project.id}/`) return project
  if (endpoint === 'v1/rates/') return [{ id: 'demo-rate', description: 'Índice demonstrativo', index: 'Índice demonstrativo' }]
  if (endpoint === 'v1/rates/templates/') return [{ classe: { classe: 'I' }, templates: [{ id: 'demo-template', name: 'Crédito demonstrativo' }] }]
  if (endpoint === 'v1/files/example/project/') return { excelNames: ['modelo-credores.xlsx'] }
  if (endpoint.includes('files/detail/project/')) return { files: [] }
  if (endpoint.includes('options')) return { options }
  if (endpoint === `v1/creditors/detail/${creditors[0].id}/`) return creditors[0]
  if (endpoint.includes('creditors') && (endpoint.includes('recovering') || endpoint.includes('project'))) return pagination(creditors)
  if (endpoint === `v1/calculation/${calculation.id}/`) return calculation
  if (endpoint.includes('check_step')) return { data: {} }
  if (endpoint.includes('calculation/creditor')) return { calculations: [calculation] }
  if (endpoint.includes('statement')) return { statement: {}, statementPf: {}, statementPj: {} }
  return []
}

const generated = ['frontend/src/auto-imports.d.ts', 'frontend/src/components.d.ts']
const snapshots = await Promise.all(generated.map(name => readFile(path.join(root, name))))
let browser
let log = ''
const server = spawn(process.execPath, [path.join(root, 'frontend/node_modules/vite/bin/vite.js'),
  '--config', path.join(output, 'vite.config.ts'), '--mode', 'documentation'], {
  cwd: path.join(root, 'frontend'), windowsHide: true,
  env: { ...process.env, VITE_API_HOST: origin, VITE_API_BASE_URL: '/calculadora-judicial/api',
    npm_package_version: JSON.parse(await readFile(path.join(root, 'frontend/package.json'), 'utf8')).version,
    VITE_BASE_URL: origin, VITE_ROUTER_BASE_URL: '/calculadora-judicial',
    VITE_TOKEN: '', VITE_LOG: 'false', VITE_LOG_REQUEST: 'false', VITE_LOG_RESPONSE: 'false' },
})
server.stdout.on('data', data => { log += data; process.stdout.write(data) })
server.stderr.on('data', data => { log += data; process.stderr.write(data) })
try {
  for (let attempt = 0; ; attempt++) {
    try { if ((await fetch(origin)).ok) break } catch {}
    if (attempt >= 90 || server.exitCode !== null) throw new Error(`Preview failed: ${log}`)
    await new Promise(resolve => setTimeout(resolve, 1000))
  }
  browser = await chromium.launch({ channel: 'chrome', headless: true })
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'pt-BR' })
  await context.addInitScript(value => sessionStorage.setItem('calculadora-user', JSON.stringify(value)), user)
  await context.route('**/calculadora-judicial/api/**', route => route.fulfill({ json: response(route.request().url()) }))
  const page = await context.newPage()
  const pageErrors = []
  page.on('pageerror', error => { pageErrors.push(error.message); console.error(`Browser: ${error.message}`) })
  await mkdir(output, { recursive: true })
  async function capture(name, route, heading) {
    await page.goto(`${origin}/calculadora-judicial${route}`, { waitUntil: 'networkidle' })
    await page.getByText(heading, { exact: false }).first().waitFor({ timeout: 20000 })
    await page.evaluate(() => document.fonts.ready)
    if (name === '05-credores.png') {
      await page.getByText('Empresa Exemplo Ltda.', { exact: true }).first().click()
      await page.getByText('Credor Exemplo A', { exact: true }).first().waitFor()
    }
    await page.locator('img[src$="/logo/calculator.svg"]').waitFor({ state: 'visible' })
    if (await page.locator('img[src$="/logo/app.svg"]').count()) throw new Error('Legacy logo remains in the navigation')
    await page.mouse.move(0, 0)
    await page.waitForTimeout(250)
    const overflows = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
    if (overflows) throw new Error(`Horizontal overflow in ${name}`)
    await page.screenshot({ path: path.join(output, name), fullPage: false, animations: 'disabled' })
    console.log(`Captured ${name}`)
  }
  await capture('01-inicio.png', '/', 'Sistema de Administração Judicial')
  await capture('02-projetos.png', '/projetos', 'Status dos projetos')
  await capture('03-time.png', '/time', 'Modo Pessoas')
  await capture('04-projeto.png', `/projeto/${project.id}`, 'Quantidade Total de Credores')
  await capture('05-credores.png', `/projeto/${project.id}/credores`, 'Credores')
  await capture('06-calculo.png', `/projeto/${project.id}/credor/${creditors[0].id}/calculo/${calculation.id}`, 'Cálculo #001')
  const calculationRoute = `/projeto/${project.id}/credor/${creditors[0].id}/calculo/${calculation.id}`
  async function captureModal(name, route, button, title, prepare) {
    await page.goto(`${origin}/calculadora-judicial${route}`, { waitUntil: 'networkidle' })
    await page.getByRole('button', { name: button, exact: true }).first().click()
    let modal = page.locator('.fixed.inset-0.opacity-100')
    await modal.getByText(title, { exact: false }).first().waitFor()
    if (prepare) await prepare(modal)
    await page.mouse.move(0, 0)
    await page.waitForTimeout(800)
    await page.screenshot({ path: path.join(output, name), fullPage: false, animations: 'disabled' })
    console.log(`Captured ${name}`)
  }
  await captureModal('07-novo-credito.png', calculationRoute, 'Novo Crédito', 'Criar Novo Credito')
  await captureModal('08-editar-calculo.png', calculationRoute, 'Editar Cálculo', 'Edição do Cálculo')
  await captureModal('09-alterar-status.png', calculationRoute, 'Alterar Status', 'Histórico do Cálculo', async modal => {
    await modal.getByRole('button', { name: 'Alterar Status', exact: true }).click()
    await modal.getByText('Enviar para Status', { exact: true }).waitFor()
  })
  await captureModal('10-novo-credor.png', `/projeto/${project.id}/credores`, 'Novo Credor', 'Cadastro de Credor')
  await captureModal('11-carregar-credores.png', `/projeto/${project.id}/credores`, 'Carregar Credores', 'Carregamento em massa de credores')
  await captureModal('12-editar-projeto.png', `/projeto/${project.id}`, 'Editar', 'Edição do Projeto')
  await captureModal('13-participantes.png', `/projeto/${project.id}`, 'Participantes', 'Participantes')
  await captureModal('14-novo-projeto.png', '/projetos', 'Novo Projeto', 'Cadastro de Projeto')
  if (pageErrors.length) throw new Error(`Browser errors: ${pageErrors.join('; ')}`)
} finally {
  await browser?.close()
  server.kill()
  await Promise.all(generated.map((name, index) => writeFile(path.join(root, name), snapshots[index])))
}
