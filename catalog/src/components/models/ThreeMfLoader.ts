import * as THREE from "three";
import { read3mf } from "@/lib/read3mf";

/** read3mf as a three Loader, so react-three-fiber's useLoader can cache and suspend on it. */
export class ThreeMfLoader extends THREE.Loader<THREE.Group> {
  load(
    url: string,
    onLoad: (group: THREE.Group) => void,
    onProgress?: (event: ProgressEvent) => void,
    onError?: (err: unknown) => void,
  ): void {
    const files = new THREE.FileLoader(this.manager);
    files.setResponseType("arraybuffer");
    files.setPath(this.path);
    files.setRequestHeader(this.requestHeader);
    files.setWithCredentials(this.withCredentials);
    files.load(
      url,
      (buffer) => {
        try {
          onLoad(this.parse(buffer as ArrayBuffer));
        } catch (err) {
          if (onError) onError(err);
          this.manager.itemError(url);
        }
      },
      onProgress,
      onError,
    );
  }

  parse(buffer: ArrayBuffer): THREE.Group {
    const group = new THREE.Group();
    for (const part of read3mf(new Uint8Array(buffer))) {
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute("position", new THREE.BufferAttribute(part.positions, 3));
      geometry.setIndex(new THREE.BufferAttribute(part.indices, 1));
      const mesh = new THREE.Mesh(geometry);
      mesh.applyMatrix4(new THREE.Matrix4().fromArray(part.matrix));
      group.add(mesh);
    }
    return group;
  }
}
