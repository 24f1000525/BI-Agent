import { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function ThreeBackground() {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2))

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
    camera.position.z = 30

    const nodeGeo = new THREE.SphereGeometry(0.12, 8, 8)
    const nodeColors = [0x3b82f6, 0x06b6d4, 0x8b5cf6, 0x10b981]
    const nodes = []
    for (let i = 0; i < 100; i++) {
      const mat = new THREE.MeshBasicMaterial({
        color: nodeColors[i % 4],
        transparent: true,
        opacity: Math.random() * 0.6 + 0.2,
      })
      const mesh = new THREE.Mesh(nodeGeo, mat)
      mesh.position.set(
        (Math.random() - 0.5) * 80,
        (Math.random() - 0.5) * 50,
        (Math.random() - 0.5) * 40
      )
      mesh.userData = {
        vx: (Math.random() - 0.5) * 0.025,
        vy: (Math.random() - 0.5) * 0.025,
        vz: (Math.random() - 0.5) * 0.015,
      }
      scene.add(mesh)
      nodes.push(mesh)
    }

    const grid = new THREE.GridHelper(100, 30, 0x1a3a6b, 0x0d2040)
    grid.position.y = -18
    grid.rotation.x = Math.PI * 0.05
    scene.add(grid)

    const lineMat = new THREE.LineBasicMaterial({ color: 0x1a3a6b, transparent: true, opacity: 0.25 })
    for (let i = 0; i < 35; i++) {
      const pts = [
        new THREE.Vector3((Math.random() - 0.5) * 80, (Math.random() - 0.5) * 50, (Math.random() - 0.5) * 40),
        new THREE.Vector3((Math.random() - 0.5) * 80, (Math.random() - 0.5) * 50, (Math.random() - 0.5) * 40),
      ]
      scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineMat))
    }

    const mkTorus = (r, t, c, px, py, pz) => {
      const m = new THREE.Mesh(
        new THREE.TorusGeometry(r, t, 8, 80),
        new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.2 })
      )
      m.position.set(px, py, pz)
      scene.add(m)
      return m
    }
    const t1 = mkTorus(8, 0.05, 0x2563eb, 18, 5, -15)
    const t2 = mkTorus(12, 0.04, 0x8b5cf6, -22, -8, -20)
    const t3 = mkTorus(5, 0.04, 0x06b6d4, 0, 15, -25)

    let mx = 0, my = 0
    const onMouseMove = (e) => {
      mx = (e.clientX / innerWidth - 0.5) * 2
      my = -(e.clientY / innerHeight - 0.5) * 2
    }
    const onResize = () => {
      renderer.setSize(innerWidth, innerHeight)
      camera.aspect = innerWidth / innerHeight
      camera.updateProjectionMatrix()
    }
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('resize', onResize)

    let animId
    const animate = () => {
      animId = requestAnimationFrame(animate)
      nodes.forEach(n => {
        n.position.x += n.userData.vx
        n.position.y += n.userData.vy
        n.position.z += n.userData.vz
        if (Math.abs(n.position.x) > 40) n.userData.vx *= -1
        if (Math.abs(n.position.y) > 25) n.userData.vy *= -1
        if (Math.abs(n.position.z) > 20) n.userData.vz *= -1
      })
      t1.rotation.x += 0.003; t1.rotation.y += 0.002
      t2.rotation.y += 0.004; t2.rotation.z += 0.002
      t3.rotation.x += 0.005; t3.rotation.z += 0.003
      camera.position.x += (mx * 3 - camera.position.x) * 0.02
      camera.position.y += (my * 2 - camera.position.y) * 0.02
      camera.lookAt(scene.position)
      renderer.render(scene, camera)
    }
    animate()

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('resize', onResize)
      renderer.dispose()
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      style={{ position: 'fixed', inset: 0, zIndex: 0, opacity: 0.8, pointerEvents: 'none' }}
    />
  )
}
