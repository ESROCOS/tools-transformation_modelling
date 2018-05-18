# ======================================================================
#  FILE:  $URL$
# ======================================================================
#  PROJECT:             :  ESROCOS
#  VERSION              :  $Revision$
#  LANGUAGE             :  CMake script
#  AUTHOR               :  $LastChangedBy$ 
#  COPYRIGHT            :  DFKI GmbH
#  COMPILER             :  cmake version 3.0.2
#  CREATED              :  $CreationDate$
#  CLASS                :  -
#  LAST MODIFIED        :  $LastChangedDate$
#  GENERATED FROM MODEL :  -
#  ORIGINAL MODEL AUTHOR:  -
# ----------------------------------------------------------------------
#  Toplevel CMake build script for the asn1_types library
# ----------------------------------------------------------------------
#  HISTORY
#  $History$
# ======================================================================

# CMakeLists.txt has to be located in the project folder and cmake has to be
# executed from 'project/build' with 'cmake ../'.
cmake_minimum_required(VERSION 2.6)

project(esrocos_transformer_modelling_tool)

file(GLOB tool
     "${CMAKE_SOURCE_DIR}/bin/esrocos_transformation_annotation_tool"
)

set(PERMISSIONS_DEFAULT
    OWNER_WRITE OWNER_READ OWNER_EXECUTE
    GROUP_READ GROUP_EXECUTE
    WORLD_READ WORLD_EXECUTE)

install(FILES ${tool}
	DESTINATION ${CMAKE_INSTALL_PREFIX}/bin
	PERMISSIONS ${PERMISSIONS_DEFAULT})

message(STATUS "installed tools")
