// SPDX-License-Identifier: Apache-2.0

import * as THREE from 'three';
import type { UrdfVisual } from './urdf-parser';

export interface MaterialSpec {
  name?: string;
  color: THREE.Color;
  opacity: number;
  metalness: number;
  roughness: number;
  transmission: number;
  thickness: number;
  ior: number;
  clearcoat: number;
  clearcoatRoughness: number;
  envMapIntensity: number;
  pbr?: {
    baseColorTexture?: string;
    normalTexture?: string;
    roughnessTexture?: string;
    metallicTexture?: string;
    displacementTexture?: string;
    projection: 'uv' | 'triplanar';
    repeat: [number, number];
    scale: number;
    normalScale: number;
  };
}

export interface LoadedPbrTextures {
  baseColor?: THREE.Texture;
  normal?: THREE.Texture;
  roughness?: THREE.Texture;
  metallic?: THREE.Texture;
  displacement?: THREE.Texture;
}

const textureTemplateCache = new Map<string, Promise<THREE.Texture>>();

function appendRevisionParam(url: string, assetRevisionKey: string | null | undefined): string {
  if (!assetRevisionKey) {
    return url;
  }
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}rev=${encodeURIComponent(assetRevisionKey)}`;
}

function resolveTextureUrl(
  filename: string,
  baseUrl: string,
  assetRevisionKey: string | null | undefined,
): string {
  const url = baseUrl.endsWith('/') ? `${baseUrl}${filename}` : `${baseUrl}/${filename}`;
  return appendRevisionParam(url, assetRevisionKey);
}

async function loadTextureTemplate(url: string): Promise<THREE.Texture> {
  const cached = textureTemplateCache.get(url);
  if (cached) {
    return cached;
  }
  const pending = new THREE.TextureLoader().loadAsync(url);
  textureTemplateCache.set(url, pending);
  void pending.catch(() => {
    if (textureTemplateCache.get(url) === pending) {
      textureTemplateCache.delete(url);
    }
  });
  return pending;
}

async function loadTexture(
  filename: string | undefined,
  baseUrl: string,
  assetRevisionKey: string | null | undefined,
  colorSpace: THREE.ColorSpace,
): Promise<THREE.Texture | undefined> {
  if (!filename) {
    return undefined;
  }
  const template = await loadTextureTemplate(resolveTextureUrl(filename, baseUrl, assetRevisionKey));
  const texture = template.clone();
  texture.colorSpace = colorSpace;
  texture.needsUpdate = true;
  return texture;
}

export async function loadPbrTextures(
  spec: MaterialSpec,
  baseUrl: string,
  assetRevisionKey?: string | null,
): Promise<LoadedPbrTextures | undefined> {
  if (!spec.pbr) {
    return undefined;
  }
  const [baseColor, normal, roughness, metallic, displacement] = await Promise.all([
    loadTexture(spec.pbr.baseColorTexture, baseUrl, assetRevisionKey, THREE.SRGBColorSpace),
    loadTexture(spec.pbr.normalTexture, baseUrl, assetRevisionKey, THREE.NoColorSpace),
    loadTexture(spec.pbr.roughnessTexture, baseUrl, assetRevisionKey, THREE.NoColorSpace),
    loadTexture(spec.pbr.metallicTexture, baseUrl, assetRevisionKey, THREE.NoColorSpace),
    loadTexture(spec.pbr.displacementTexture, baseUrl, assetRevisionKey, THREE.NoColorSpace),
  ]);
  return { baseColor, normal, roughness, metallic, displacement };
}

export function depthBiasForOrdinal(ordinal: number): number {
  return 1 + ordinal * 0.25;
}

function srgbColor(r: number, g: number, b: number): THREE.Color {
  return new THREE.Color().setRGB(r, g, b, THREE.SRGBColorSpace);
}

function softenBrightDiffuse(spec: MaterialSpec): void {
  const maxChannel = Math.max(spec.color.r, spec.color.g, spec.color.b);
  const minChannel = Math.min(spec.color.r, spec.color.g, spec.color.b);
  const isBrightNeutral = maxChannel > 0.78 && maxChannel - minChannel < 0.08;

  if (!isBrightNeutral || spec.metalness > 0.2 || spec.transmission > 0.01) {
    return;
  }

  spec.color.lerp(new THREE.Color(0.82, 0.82, 0.78), 0.38);
  spec.roughness = Math.max(spec.roughness, 0.62);
  spec.clearcoat = Math.min(spec.clearcoat, 0.08);
  spec.envMapIntensity = Math.min(spec.envMapIntensity, 0.55);
}

/**
 * Resolve visual material specification from URDF data
 * Defaults to a neutral gray if no material specified
 */
export function resolveVisualMaterialSpec(visual: UrdfVisual): MaterialSpec {
  const defaultSpec: MaterialSpec = {
    name: undefined,
    color: srgbColor(0.74, 0.74, 0.72),
    opacity: 1.0,
    metalness: 0.05,
    roughness: 0.48,
    transmission: 0,
    thickness: 0,
    ior: 1.45,
    clearcoat: 0,
    clearcoatRoughness: 0.2,
    envMapIntensity: 0.8,
  };

  if (!visual.material) {
    return defaultSpec;
  }

  const spec = { ...defaultSpec };
  spec.name = visual.material.name;

  if (visual.material.color) {
    const [r, g, b, a] = visual.material.color.rgba;
    spec.color = srgbColor(r, g, b);
    spec.opacity = a;
  }

  if (visual.material.texture?.filename) {
    spec.pbr = {
      baseColorTexture: visual.material.texture.filename,
      normalTexture: visual.material.pbr?.normalTexture,
      roughnessTexture: visual.material.pbr?.roughnessTexture,
      metallicTexture: visual.material.pbr?.metallicTexture,
      displacementTexture: visual.material.pbr?.displacementTexture,
      projection: visual.material.pbr?.projection ?? 'uv',
      repeat: visual.material.pbr?.repeat ?? [1, 1],
      scale: visual.material.pbr?.scale ?? 1,
      normalScale: visual.material.pbr?.normalScale ?? 1,
    };
  }

  const tuned = applyNamedMaterialPreset(spec);
  softenBrightDiffuse(tuned);
  return tuned;
}

function applyNamedMaterialPreset(spec: MaterialSpec): MaterialSpec {
  const name = spec.name?.toLowerCase() ?? '';
  const tuned = { ...spec };
  const tokens = name.split(/[^a-z0-9]+/).filter(Boolean);
  const hasToken = (token: string): boolean => tokens.includes(token);
  const hasAnyToken = (...candidates: string[]): boolean => candidates.some(hasToken);
  const mentionsTransparentDescriptor = hasAnyToken(
    'clear',
    'glass',
    'transparent',
    'translucent',
    'smoked',
    'frosted',
  );
  const mentionsTransparentPlasticFamily = hasAnyToken(
    'polycarbonate',
    'acrylic',
    'plexi',
    'plexiglass',
    'lexan',
  );
  const isClearRigidMaterial = (
    mentionsTransparentDescriptor
    || (mentionsTransparentPlasticFamily && tuned.opacity < 0.999)
  );

  if (isClearRigidMaterial) {
    tuned.metalness = 0.0;
    tuned.roughness = 0.08;
    tuned.transmission = Math.max(0.45, 1.0 - tuned.opacity * 0.55);
    tuned.thickness = 0.006;
    tuned.ior = 1.45;
    tuned.clearcoat = 0.9;
    tuned.clearcoatRoughness = 0.06;
    tuned.envMapIntensity = 1.25;
    return tuned;
  }

  if (name.includes('reflector')) {
    tuned.metalness = 0.9;
    tuned.roughness = 0.18;
    tuned.opacity = Math.max(tuned.opacity, 0.78);
    tuned.clearcoat = 0.18;
    tuned.clearcoatRoughness = 0.12;
    tuned.envMapIntensity = 1.4;
    return tuned;
  }

  if (name.includes('brass') || name.includes('metal')) {
    tuned.metalness = 0.88;
    tuned.roughness = 0.22;
    tuned.clearcoat = 0.16;
    tuned.clearcoatRoughness = 0.18;
    tuned.envMapIntensity = 1.3;
    return tuned;
  }

  if (name.includes('bakelite')) {
    tuned.metalness = 0.02;
    tuned.roughness = 0.38;
    tuned.clearcoat = 0.24;
    tuned.clearcoatRoughness = 0.2;
    tuned.envMapIntensity = 0.7;
    return tuned;
  }

  if (name.includes('felt')) {
    tuned.metalness = 0.0;
    tuned.roughness = 0.92;
    tuned.clearcoat = 0.0;
    tuned.envMapIntensity = 0.25;
  }

  return tuned;
}

/**
 * Create a THREE.js material from a material spec
 */
export function createMaterial(spec: MaterialSpec, options?: {
  wireframe?: boolean;
  transparent?: boolean;
  side?: THREE.Side;
  depthBias?: number;
}): THREE.MeshPhysicalMaterial {
  const transparent = options?.transparent ?? (spec.opacity < 0.999 || spec.transmission > 0.01);
  const side = options?.side ?? THREE.FrontSide;
  const depthBias = options?.depthBias ?? 0;

  return new THREE.MeshPhysicalMaterial({
    color: spec.color,
    opacity: spec.opacity,
    metalness: spec.metalness,
    roughness: spec.roughness,
    transmission: spec.transmission,
    thickness: spec.thickness,
    ior: spec.ior,
    clearcoat: spec.clearcoat,
    clearcoatRoughness: spec.clearcoatRoughness,
    envMapIntensity: spec.envMapIntensity,
    transparent,
    depthWrite: !transparent,
    forceSinglePass: transparent,
    wireframe: options?.wireframe ?? false,
    side,
    polygonOffset: depthBias !== 0,
    polygonOffsetFactor: 0,
    polygonOffsetUnits: depthBias,
  });
}

function configureUvPbrMaterial(
  material: THREE.MeshPhysicalMaterial,
  spec: MaterialSpec,
  textures: LoadedPbrTextures,
): void {
  if (!spec.pbr) {
    return;
  }
  material.userData.articraftPbrTextures = textures;
  const repeat = spec.pbr.repeat;
  for (const texture of Object.values(textures)) {
    if (!texture) {
      continue;
    }
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.repeat.set(repeat[0], repeat[1]);
    texture.needsUpdate = true;
  }
  material.map = textures.baseColor ?? null;
  material.normalMap = textures.normal ?? null;
  material.normalScale.set(spec.pbr.normalScale, spec.pbr.normalScale);
  material.roughnessMap = textures.roughness ?? null;
  if (textures.roughness) {
    material.roughness = 1;
  }
  material.metalnessMap = textures.metallic ?? null;
  if (textures.metallic) {
    material.metalness = 1;
  }
  material.needsUpdate = true;
}

function configureTriplanarPbrMaterial(
  material: THREE.MeshPhysicalMaterial,
  spec: MaterialSpec,
  textures: LoadedPbrTextures,
): void {
  if (!spec.pbr || !textures.baseColor) {
    return;
  }
  material.userData.articraftPbrTextures = textures;

  for (const texture of Object.values(textures)) {
    if (!texture) {
      continue;
    }
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.needsUpdate = true;
  }

  const baseColor = textures.baseColor;
  const normal = textures.normal ?? textures.baseColor;
  const roughness = textures.roughness ?? textures.baseColor;
  const metallic = textures.metallic ?? textures.baseColor;
  const scale = spec.pbr.scale;
  const normalScale = spec.pbr.normalScale;

  material.onBeforeCompile = (shader) => {
    shader.uniforms.articraftTriColor = { value: baseColor };
    shader.uniforms.articraftTriNormal = { value: normal };
    shader.uniforms.articraftTriRoughness = { value: roughness };
    shader.uniforms.articraftTriMetallic = { value: metallic };
    shader.uniforms.articraftTriScale = { value: scale };
    shader.uniforms.articraftTriNormalScale = { value: normalScale };

    shader.vertexShader = shader.vertexShader
      .replace(
        '#include <common>',
        `#include <common>\nvarying vec3 vArticraftTriPosition;\nvarying vec3 vArticraftTriNormal;`,
      )
      .replace(
        '#include <begin_vertex>',
        `#include <begin_vertex>\nvArticraftTriPosition = position;\nvArticraftTriNormal = normal;`,
      );

    shader.fragmentShader = shader.fragmentShader
      .replace(
        '#include <common>',
        `#include <common>
uniform sampler2D articraftTriColor;
uniform sampler2D articraftTriNormal;
uniform sampler2D articraftTriRoughness;
uniform sampler2D articraftTriMetallic;
uniform float articraftTriScale;
uniform float articraftTriNormalScale;
uniform mat3 normalMatrix;
varying vec3 vArticraftTriPosition;
varying vec3 vArticraftTriNormal;

vec3 articraftTriWeights(vec3 objectNormal) {
  vec3 weights = pow(abs(normalize(objectNormal)), vec3(6.0));
  return weights / max(weights.x + weights.y + weights.z, 0.00001);
}

vec2 articraftTriUvX(vec3 p, vec3 n) { return vec2(p.y * sign(n.x), p.z); }
vec2 articraftTriUvY(vec3 p, vec3 n) { return vec2(-p.x * sign(n.y), p.z); }
vec2 articraftTriUvZ(vec3 p, vec3 n) { return vec2(p.x * sign(n.z), p.y); }

vec4 articraftTriSample(sampler2D tex, vec3 p, vec3 n, vec3 weights) {
  vec4 sampleX = texture2D(tex, articraftTriUvX(p, n));
  vec4 sampleY = texture2D(tex, articraftTriUvY(p, n));
  vec4 sampleZ = texture2D(tex, articraftTriUvZ(p, n));
  return sampleX * weights.x + sampleY * weights.y + sampleZ * weights.z;
}

vec3 articraftTriNormalSample(vec3 p, vec3 n, vec3 weights) {
  vec3 nx = texture2D(articraftTriNormal, articraftTriUvX(p, n)).xyz * 2.0 - 1.0;
  vec3 ny = texture2D(articraftTriNormal, articraftTriUvY(p, n)).xyz * 2.0 - 1.0;
  vec3 nz = texture2D(articraftTriNormal, articraftTriUvZ(p, n)).xyz * 2.0 - 1.0;
  vec3 objectX = vec3(nx.z * sign(n.x), nx.x * sign(n.x), nx.y);
  vec3 objectY = vec3(-ny.x * sign(n.y), ny.z * sign(n.y), ny.y);
  vec3 objectZ = vec3(nz.x * sign(n.z), nz.y, nz.z * sign(n.z));
  return normalize(objectX * weights.x + objectY * weights.y + objectZ * weights.z);
}`,
      )
      .replace(
        '#include <map_fragment>',
        `vec3 articraftTriP = vArticraftTriPosition * articraftTriScale;
vec3 articraftTriW = articraftTriWeights(vArticraftTriNormal);
diffuseColor *= articraftTriSample(articraftTriColor, articraftTriP, vArticraftTriNormal, articraftTriW);`,
      )
      .replace(
        '#include <roughnessmap_fragment>',
        `float roughnessFactor = roughness;
roughnessFactor *= articraftTriSample(
  articraftTriRoughness,
  vArticraftTriPosition * articraftTriScale,
  vArticraftTriNormal,
  articraftTriWeights(vArticraftTriNormal)
).r;`,
      )
      .replace(
        '#include <metalnessmap_fragment>',
        `float metalnessFactor = metalness;
metalnessFactor *= articraftTriSample(
  articraftTriMetallic,
  vArticraftTriPosition * articraftTriScale,
  vArticraftTriNormal,
  articraftTriWeights(vArticraftTriNormal)
).r;`,
      )
      .replace(
        '#include <normal_fragment_maps>',
        `#include <normal_fragment_maps>
vec3 articraftObjectNormal = articraftTriNormalSample(
  vArticraftTriPosition * articraftTriScale,
  vArticraftTriNormal,
  articraftTriWeights(vArticraftTriNormal)
);
normal = normalize(mix(normal, normalMatrix * articraftObjectNormal, articraftTriNormalScale));`,
      );
  };
  material.customProgramCacheKey = () => `articraft-triplanar-v1-${scale}-${normalScale}`;
  material.roughness = 1;
  material.metalness = 1;
  material.needsUpdate = true;
}

export function applyPbrTextures(
  material: THREE.MeshPhysicalMaterial,
  spec: MaterialSpec,
  textures: LoadedPbrTextures | undefined,
): void {
  if (!textures || !spec.pbr) {
    return;
  }
  if (spec.pbr.projection === 'triplanar') {
    configureTriplanarPbrMaterial(material, spec, textures);
    return;
  }
  configureUvPbrMaterial(material, spec, textures);
}

/**
 * Create edge lines for a geometry
 */
export function createEdgeLines(geometry: THREE.BufferGeometry, color: number = 0x000000): THREE.LineSegments {
  const edges = new THREE.EdgesGeometry(geometry, 15); // 15 degree threshold
  const lineMaterial = new THREE.LineBasicMaterial({ color, opacity: 0.3, transparent: true });
  return new THREE.LineSegments(edges, lineMaterial);
}
