package com.devctl.backendtest.mapper;

import com.devctl.backendtest.dto.request.TestRequest;
import com.devctl.backendtest.dto.response.TestResponse;
import com.devctl.backendtest.entity.TestEntity;
import javax.annotation.processing.Generated;
import org.springframework.stereotype.Component;

@Generated(
    value = "org.mapstruct.ap.MappingProcessor",
    date = "2026-05-12T14:45:05+0100",
    comments = "version: 1.5.5.Final, compiler: javac, environment: Java 21.0.11 (Eclipse Adoptium)"
)
@Component
public class TestMapperImpl implements TestMapper {

    @Override
    public TestResponse toResponse(TestEntity entity) {
        if ( entity == null ) {
            return null;
        }

        TestResponse.TestResponseBuilder testResponse = TestResponse.builder();

        testResponse.id( entity.getId() );
        testResponse.name( entity.getName() );

        return testResponse.build();
    }

    @Override
    public TestEntity toEntity(TestRequest request) {
        if ( request == null ) {
            return null;
        }

        TestEntity testEntity = new TestEntity();

        testEntity.setName( request.getName() );

        return testEntity;
    }

    @Override
    public void updateEntityFromRequest(TestRequest request, TestEntity entity) {
        if ( request == null ) {
            return;
        }

        entity.setName( request.getName() );
    }
}
