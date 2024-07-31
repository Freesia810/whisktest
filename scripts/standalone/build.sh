cd ..
pushd openwhisk
./gradlew :core:standalone:build

cp bin/openwhisk-standalone.jar ../bin

popd
