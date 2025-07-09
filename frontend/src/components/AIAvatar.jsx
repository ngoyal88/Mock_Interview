import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';

const AvatarModel = ({ url }) => {
  const { scene } = useGLTF(url);
  return <primitive object={scene} scale={1.5} position={[0, -1.5, 0]} />;
};

const AIAvatar = ({ modelUrl }) => {
  return (
    <div className="w-full h-full bg-black rounded-lg overflow-hidden">
      <Canvas camera={{ position: [0, 1, 3], fov: 30 }}>
        <ambientLight intensity={1} />
        <directionalLight position={[5, 5, 5]} intensity={1} />
        <Suspense fallback={null}>
          <AvatarModel url={modelUrl} />
        </Suspense>
        <OrbitControls enableZoom={false} />
      </Canvas>
    </div>
  );
};

export default AIAvatar;
